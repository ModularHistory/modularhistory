from typing import Type

from apps.moderation.models import Change
from apps.moderation.models.moderated_model.model import ModeratedModel
from apps.moderation.moderator import GenericModerator

from .constants import DraftState, ModerationStatus


class ModerationManager:
    def register(self, model_class, moderator_class=None):
        """Registers model class with moderation"""
        if moderator_class is None:
            moderator_class = GenericModerator

        if not issubclass(moderator_class, GenericModerator):
            msg = (
                'moderator_class must subclass '
                'GenericModerator class, found %s' % moderator_class
            )
            raise AttributeError(msg)

        moderator_class_instance = moderator_class(model_class)

        try:
            # Any of this stuff could fail, and we don't want to register the
            # model if these aren't successful, so we wrap it with a
            # try/except/else block
            self._connect_signals(model_class)
        except Exception:
            raise
        else:
            self._registered_models[model_class] = moderator_class_instance

    def _connect_signals(self, model_class):
        from django.db.models import signals

        signals.pre_save.connect(self.pre_save_handler, sender=model_class)
        signals.post_save.connect(self.post_save_handler, sender=model_class)

    def unregister(self, model_class):
        """Unregister model class from moderation"""
        moderator_instance = self._registered_models[model_class]

        # Any of this stuff could fail, and we don't want to unregister the
        # model if these aren't successful, so we wrap it with a
        # try/except/else block
        try:
            self._remove_fields(moderator_instance)
            self._disconnect_signals(model_class)
        except Exception:
            raise
        else:
            self._registered_models.pop(model_class)

    def _remove_fields(self, moderator_class_instance):
        """Removes fields from model class and disconnects signals"""

        model_class = moderator_class_instance.model_class

        moderated_manager_indexes = [
            i
            for i, m in enumerate(model_class._meta.local_managers)
            if not m.name.startswith('unmoderated_')
        ]

        managers = [
            m
            for i, m in enumerate(model_class._meta.local_managers)
            if i not in moderated_manager_indexes
        ]

        for m in managers:
            m.name = m.name.replace('unmoderated_', '')

        model_class._meta.local_managers = managers

        delattr(model_class, 'moderation')

        model_class._meta._expire_cache()

    def _disconnect_signals(self, model_class):
        from django.db.models import signals

        signals.pre_save.disconnect(self.pre_save_handler, model_class)
        signals.post_save.disconnect(self.post_save_handler, model_class)

    def pre_save_handler(self, sender: Type[ModeratedModel], instance, **kwargs):
        """
        Create a new moderation for the instance if it doesn't have any.
        If it does have a previous moderation, get that one
        """
        # check if object was loaded from fixture, bypass moderation if so
        if kwargs['raw']:
            return

        unchanged_obj = self._get_unchanged_object(instance)
        moderator = sender.Moderator(sender)
        if unchanged_obj:
            moderated_obj = self._get_or_create_moderation(instance, unchanged_obj, moderator)
            if not (
                moderated_obj.moderation_status == ModerationStatus.APPROVED
                or moderator.bypass_moderation_after_approval
            ):
                moderated_obj.save()

    def _get_unchanged_object(self, instance):
        if instance.pk is None:
            return None
        pk = instance.pk
        try:
            unchanged_obj = instance.__class__._default_unmoderated_manager.get(pk=pk)
            return unchanged_obj
        except instance.__class__.DoesNotExist:
            return None

    def _get_updated_object(self, instance, unchanged_obj, moderator):
        """
        Returns the unchanged object with the excluded fields updated to
        those from the instance.
        """
        excludes = moderator.fields_exclude
        for field in instance._meta.fields:
            if field.name in excludes:
                value = getattr(instance, field.name)
                setattr(unchanged_obj, field.name, value)

        return unchanged_obj

    def _get_or_create_moderation(self, instance, unchanged_obj, moderator):
        """
        Get or create Moderation instance.
        If moderated object is not equal instance then serialize unchanged
        in moderated object in order to use it later in post_save_handler
        """

        def get_new_instance(unchanged_obj):
            moderation = Change(content_object=unchanged_obj)
            moderation.changed_object = unchanged_obj
            return moderation

        try:
            moderation = Change.objects.get_for_instance(instance)
            if moderation is None:
                moderation = get_new_instance(unchanged_obj)
            elif moderator.keep_history and moderation.has_object_been_changed(instance):
                # We're keeping history and this isn't an update of an existing
                # moderation
                moderation = get_new_instance(unchanged_obj)

        except Change.DoesNotExist:
            moderation = get_new_instance(unchanged_obj)

        else:
            if moderation.has_object_been_changed(instance):
                moderation.changed_object = self._get_updated_object(
                    instance, unchanged_obj, moderator
                )
            elif moderation.has_object_been_changed(instance, only_excluded=True):
                moderation.changed_object = self._get_updated_object(
                    instance, unchanged_obj, moderator
                )

        return moderation

    def get_moderator(self, model_class: Type[ModeratedModel]):
        return model_class.Moderator(model_class)

    def post_save_handler(self, sender, instance, **kwargs):
        """
        Creates new moderation object if instance is created,
        If instance exists and is only updated then save instance as
        content_object of moderation
        """
        # check if object was loaded from fixture, bypass moderation if so

        if kwargs['raw']:
            return

        pk = instance.pk
        moderator = self.get_moderator(sender)

        if kwargs['created_date']:
            old_object = sender._default_unmoderated_manager.get(pk=pk)
            moderated_obj = Change(content_object=old_object)
            # Hide it by placing in draft state
            moderated_obj.draft_state = DraftState.DRAFT
            moderated_obj.save()
            moderator.inform_moderator(instance)
            return

        moderated_obj = Change.objects.get_for_instance(instance)

        if (
            moderated_obj.status == ModerationStatus.APPROVED
            and moderator.bypass_moderation_after_approval
        ):
            # save new data in moderated object
            moderated_obj.changed_object = instance
            moderated_obj.save()
            return

        if moderated_obj.has_object_been_changed(instance):
            copied_instance = self._copy_model_instance(instance)
            # Save instance with old data from changed_object, undoing
            # the changes that save() just saved to the database.
            moderated_obj.changed_object.save_base(raw=True)
            # Save the new data in moderation, so it will be applied
            # to the real record when the moderator approves the change.
            moderated_obj.changed_object = copied_instance
            moderated_obj.status = ModerationStatus.PENDING
            moderated_obj.save()
            moderator.inform_moderator(instance)
            instance._moderation = moderated_obj

    def _copy_model_instance(self, obj):
        initial = dict([(f.name, getattr(obj, f.name)) for f in obj._meta.fields])
        return obj.__class__(**initial)
