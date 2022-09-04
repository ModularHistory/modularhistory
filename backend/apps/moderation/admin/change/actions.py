from typing import TYPE_CHECKING

from django.utils.translation import ugettext as _

from apps.moderation.constants import ModerationStatus

if TYPE_CHECKING:
    from django.http.request import HttpRequest

    from apps.moderation.admin.change.admin import ChangeAdmin
    from apps.moderation.models.change.queryset import ChangeQuerySet


def approve_objects(
    modeladmin: 'ChangeAdmin',
    request: 'HttpRequest',
    queryset: 'ChangeQuerySet',
):
    """Approve all changes in the queryset."""
    queryset.approve(moderator=request.user)


approve_objects.short_description = _('Approve selected changes')


def reject_objects(
    modeladmin: 'ChangeAdmin',
    request: 'HttpRequest',
    queryset: 'ChangeQuerySet',
):
    """Reject all changes in the queryset."""
    queryset.reject(moderator=request.user)


reject_objects.short_description = _('Reject selected changes')


def set_objects_as_pending(
    modeladmin: 'ChangeAdmin',
    request: 'HttpRequest',
    queryset: 'ChangeQuerySet',
):
    """Set the moderation status of all changes in the queryset to "pending"."""
    queryset.update(status=ModerationStatus.PENDING)


set_objects_as_pending.short_description = _('Set selected changes as pending')
