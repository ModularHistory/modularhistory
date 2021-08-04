from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.db.models.manager import Manager
from django.db.utils import ProgrammingError

from . import moderation
from .constants import MODERATION_READY_STATE
from .queryset import ModeratedObjectQuerySet


class MetaClass(type(Manager)):
    def __new__(cls, name, bases, attrs):
        return super(MetaClass, cls).__new__(cls, name, bases, attrs)


class ModerationObjectsManager(Manager):
    class MultipleModerations(Exception):
        def __init__(self, base_object):
            self.base_object = base_object
            super(ModerationObjectsManager.MultipleModerations, self).__init__(
                f'Multiple moderations found for object/s: {base_object}'
            )

    def __call__(self, base_manager, *args, **kwargs):
        return MetaClass(
            self.__class__.__name__,
            (self.__class__, base_manager),
            {'use_for_related_fields': True},
        )

    def filter_moderated_objects(self, queryset):
        # Find any objects that have more than one related ModeratedObject
        annotated_queryset = queryset.annotate(
            num_moderation_objects=Count('_relation_object')
        ).filter(num_moderation_objects__gt=1)

        if annotated_queryset.exists():
            # No sensible default action here. You need to override
            # filter_moderated_objects() to handle this as you see fit.
            raise self.MultipleModerations(annotated_queryset)

        only_no_relation_objects = {
            '_relation_object': None,
        }
        only_ready = {
            '_relation_object__state': MODERATION_READY_STATE,
        }
        return queryset.filter(Q(**only_no_relation_objects) | Q(**only_ready))

    def exclude_objs_by_visibility_col(self, queryset):
        return queryset.exclude(**{self.moderator.visibility_column: False})

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            if self.moderator.visibility_column:
                return self.exclude_objs_by_visibility_col(queryset)
            return self.filter_moderated_objects(queryset)
        except ProgrammingError:
            # Migrations might not have been run yet to add the ModeratedObject table.
            return queryset

    @property
    def moderator(self):
        return moderation.get_moderator(self.model)


class ModeratedObjectManager(Manager):
    def get_queryset(self):
        return ModeratedObjectQuerySet(self.model, using=self._db)

    def get_for_instance(self, instance):
        '''Returns ModeratedObject for given model instance'''
        try:
            moderated_object = self.get(
                object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance.__class__),
            )
        except self.model.MultipleObjectsReturned:
            # Get the most recent one
            moderated_object = self.filter(
                object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance.__class__),
            ).order_by('-updated')[0]
        return moderated_object
