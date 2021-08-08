from typing import Type

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from apps.admin.model_admin import ExtendedModelAdmin
from apps.moderation.constants import ModerationStatus
from apps.moderation.forms import BaseModerationForm
from apps.moderation.models.change import Change
from apps.moderation.models.moderated_model.model import ModeratedModel


class ModeratedModelAdmin(ExtendedModelAdmin):
    """Admin for models requiring moderation."""

    admin_integration_enabled = True

    # def get_queryset(self, request):
    #     # Modified from django.contrib.admin.options.BaseModelAdmin
    #     qs = self.model._default_unmoderated_manager.get_queryset()
    #     ordering = self.get_ordering(request)
    #     if ordering:
    #         qs = qs.order_by(*ordering)
    #     return qs

    def get_form(self, request, obj=None, **kwargs):
        if obj and self.admin_integration_enabled:
            self.form = self.get_moderation_form(obj.__class__)
        return super().get_form(request, obj, **kwargs)

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     # if self.admin_integration_enabled:
    #     #     self.send_message(request, object_id)
    #     try:
    #         return super().change_view(
    #             request, object_id, form_url=form_url, extra_context=extra_context
    #         )
    #     except TypeError:
    #         return super().change_view(request, object_id, extra_context=extra_context)

    # def send_message(self, request, object_id):
    #     try:
    #         obj = self.model.unmoderations.get(pk=object_id)
    #         moderated_obj = Change.objects.get_for_instance(obj)
    #         moderator = moderated_obj.moderator
    #         msg = self.get_moderation_message(moderated_obj.status, moderated_obj.reason)
    #     except Change.DoesNotExist:
    #         msg = self.get_moderation_message()

    #     self.message_user(request, msg)

    def save_model(self, request, instance: 'ModeratedModel', form, change):
        print(f'>>>> save_model')
        if self.admin_integration_enabled:
            if instance.has_change_in_progress:
                change = instance.change_in_progress
                change.object_after_change = instance
                change.save()
            else:
                change = Change.objects.create(
                    content_type=ContentType.objects.get_for_model(instance.__class__),
                    object_id=instance.pk,
                    moderation_status=ModerationStatus.PENDING,
                    object_after_change=instance,
                )
                print(f'>>>> Created change: {change}')
        else:
            instance.save()

    def get_moderation_message(self, status=None, reason=None):
        if status == ModerationStatus.PENDING:
            return _(
                'Object is not viewable on site, '
                'it will be visible if moderator accepts it'
            )
        elif status == ModerationStatus.REJECTED:
            return _(f'Object has been rejected by moderator (reason: {reason}).')
        elif status == ModerationStatus.APPROVED:
            return _('Object has been approved by moderator and is visible on site.')
        elif status is None:
            return _('This object is not registered with the moderation system.')

    def get_moderation_form(self, model_class: Type[ModeratedModel]):
        """Return the form to be used to propose changes to a moderated model instance."""

        class ModerationForm(BaseModerationForm):
            class Meta:
                model = model_class
                fields = '__all__'

        return ModerationForm
