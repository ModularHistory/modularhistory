from django.utils.translation import ugettext as _

from apps.moderation.constants import ModerationStatus


def approve_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.approve(by=request.user)


approve_objects.short_description = _('Approve selected moderated objects')


def reject_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.reject(by=request.user)


reject_objects.short_description = _('Reject selected moderated objects')


def set_objects_as_pending(modeladmin, request, queryset):
    queryset.update(status=ModerationStatus.PENDING)


set_objects_as_pending.short_description = _('Set selected moderated' ' objects as Pending')
