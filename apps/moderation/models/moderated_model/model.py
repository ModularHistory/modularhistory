import logging
from typing import TYPE_CHECKING, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_currentuser.middleware import get_current_authenticated_user

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.change.model import Change
from apps.moderation.models.contribution import ContentContribution
from apps.moderation.models.moderated_model.manager import ModeratedManager
from core.models.soft_deletable import SoftDeletableModel

if TYPE_CHECKING:

    from apps.moderation.models.changeset import ChangeSet
    from apps.users.models import User


class ModeratedModel(SoftDeletableModel):
    """Base class for models of which instances must be moderated."""

    changes = GenericRelation(to='moderation.Change')

    # This field is used to determine whether model instances have been moderated and
    # should be visible to users.
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
    )

    objects = ModeratedManager()

    class Meta:
        abstract = True

    class Moderation:
        excluded_fields = [
            'changes',
            'verified',
            'deleted',
            'cache',
            'pretty_cache',
            'date_string',
        ]

    def delete(self, **kwargs):
        """Override saving after deletion to use moderation."""
        super()._delete(on_save=self.save, **kwargs)

    def undelete(self, **kwargs):
        """Override saving after un-deletion to use moderation."""
        super()._undelete(on_save=self.save, **kwargs)

    def save(self, *args, **kwargs):
        """Override save behavior to use moderation."""
        moderate = kwargs.pop('moderate', True)
        contributor = kwargs.pop('contributor', get_current_authenticated_user())
        # Allow creation of pre-verified model instances.
        if self._state.adding and self.verified:
            return super().save(*args, **kwargs)
        elif moderate:
            if contributor:
                return self.save_change(contributor=contributor)
            raise Exception('Contributor is required when saving a moderated change.')
        super().save(*args, **kwargs)

    def save_change(
        self,
        contributor: Optional['User'] = None,
        set: Optional['ChangeSet'] = None,
        parent_change: Optional['Change'] = None,
    ) -> Change:
        """Save changes to a `Change` instance."""
        object_is_new = self._state.adding
        self.clean()
        logging.info(
            f'Saving a change: model={self.__class__.__name__} pk={self.pk}, contributor={contributor}, is_new={object_is_new}'
        )
        if object_is_new:
            self.verified = False
            super().save()
        change_in_progress = self.change_in_progress if not object_is_new else None
        if change_in_progress:
            # Save the changes to the existing in-progress `Change` instance.
            _change = change_in_progress
            ContentContribution.objects.create(
                contributor=contributor,
                change=_change,
                content_before=_change.changed_object,
                content_after=self,
            )
            _change.set = set or _change.set  # TODO
            _change.parent = parent_change or _change.parent  # TODO
            _change.update(changed_object=self)
        else:
            # Create a new `Change` instance.
            _change: Change = Change.objects.create(
                initiator=contributor,
                content_type=ContentType.objects.get_for_model(
                    # Ensure TypedModel subclasses use the content type of their base model.
                    getattr(
                        self.__class__,
                        'base_class',
                        self.__class__,
                    )
                ),
                object_id=self.pk,
                moderation_status=ModerationStatus.PENDING,
                changed_object=self,
                set=set,
                parent=parent_change,
            )
            ContentContribution.objects.create(
                contributor=contributor,
                change=_change,
                content_before=_change.unchanged_object,
                content_after=self,
            )
        return _change

    @property
    def change_in_progress(self) -> Optional['Change']:
        """Return the in-progress change for the moderated model instance."""
        return (
            self.changes.filter(moderation_status=ModerationStatus.PENDING).first()
            if self.has_change_in_progress
            else None
        )

    @property
    def has_change_in_progress(self) -> bool:
        """Return whether the moderated model instance has an in-progress change."""
        try:
            return self.changes.filter(moderation_status=ModerationStatus.PENDING).exists()
        except Exception as err:
            logging.error(err)
            return False
