from django.utils.translation import ugettext as _

from apps.moderation.constants import ModerationStatus

available_filters = 'moderation_status'


def approve_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.approve(moderator=request.user)


approve_objects.short_description = _('Approve selected change sets')


def reject_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.reject(moderator=request.user)


reject_objects.short_description = _('Reject selected change sets')


def set_objects_as_pending(modeladmin, request, queryset):
    queryset.update(status=ModerationStatus.PENDING)


set_objects_as_pending.short_description = _('Set moderation status to "Pending"')
