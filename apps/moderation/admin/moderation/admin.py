from django.utils.translation import ugettext as _

from apps.admin.model_admin import ExtendedModelAdmin
from apps.moderation.constants import (
    MODERATION_STATUS_APPROVED,
    MODERATION_STATUS_PENDING,
    MODERATION_STATUS_REJECTED,
)
from apps.moderation.forms import BaseModeratedObjectForm
from apps.moderation.helpers import automoderate
from apps.moderation.models import ModeratedObject


class ModerationAdmin(ExtendedModelAdmin):
    """Admin for models requiring moderation."""

    admin_integration_enabled = True

    def get_queryset(self, request):
        # Modified from django.contrib.admin.options.BaseModelAdmin
        qs = self.model._default_unmoderated_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        if obj and self.admin_integration_enabled:
            self.form = self.get_moderated_object_form(obj.__class__)

        return super().get_form(request, obj, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if self.admin_integration_enabled:
            self.send_message(request, object_id)

        try:
            return super().change_view(
                request, object_id, form_url=form_url, extra_context=extra_context
            )
        except TypeError:
            return super().change_view(request, object_id, extra_context=extra_context)

    def send_message(self, request, object_id):
        try:
            obj = self.model.unmoderated_objects.get(pk=object_id)
            moderated_obj = ModeratedObject.objects.get_for_instance(obj)
            moderator = moderated_obj.moderator
            msg = self.get_moderation_message(
                moderated_obj.status, moderated_obj.reason, moderator.visible_until_rejected
            )
        except ModeratedObject.DoesNotExist:
            msg = self.get_moderation_message()

        self.message_user(request, msg)

    def save_model(self, request, obj, form, change):
        obj.save()
        automoderate(obj, request.user)

    def get_moderation_message(self, status=None, reason=None, visible_until_rejected=False):
        if status == MODERATION_STATUS_PENDING:
            if visible_until_rejected:
                return _(
                    'Object is viewable on site, '
                    'it will be removed if moderator rejects it'
                )
            else:
                return _(
                    'Object is not viewable on site, '
                    'it will be visible if moderator accepts it'
                )
        elif status == MODERATION_STATUS_REJECTED:
            return _('Object has been rejected by moderator, ' 'reason: %s' % reason)
        elif status == MODERATION_STATUS_APPROVED:
            return _('Object has been approved by moderator ' 'and is visible on site')
        elif status is None:
            return _('This object is not registered with ' 'the moderation system.')

    def get_moderated_object_form(self, model_class):
        class ModeratedObjectForm(BaseModeratedObjectForm):
            class Meta:
                model = model_class
                fields = '__all__'

        return ModeratedObjectForm
