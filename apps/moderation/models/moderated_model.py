"""
    This module enables automatic Model registration with custom Moderators

    usage example:

        class MyModel(ModeratedModel):
            desc = models.TextField()

            class Moderator:
                notify_user = False

"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.moderation.moderator import GenericModerator


class ModeratedModel(models.Model):
    """Base class for models of which instances must be moderated."""

    # This field is used to decide whether model instances should be visible.
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
    )

    class Meta:
        abstract = True


class Moderator(GenericModerator):
    """Base moderator class for moderated models."""

    visibility_column = 'verified'

    # Allow multiple moderations per registered model instance.
    keep_history = True

    # Exclude fields from the object change list.
    fields_exclude = ['cache']

    auto_approve_for_staff = auto_approve_for_superusers = False

    def is_auto_approve(self, obj, user):
        """Determine whether to automatically approve a change."""
        return super().is_auto_approve(obj, user)

    def is_auto_reject(self, obj, user):
        """Determine whether to automatically reject a change."""
        return super().is_auto_reject(obj, user)
