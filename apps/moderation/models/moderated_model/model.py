import logging
from typing import TYPE_CHECKING, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.moderation.constants import ModerationStatus
from apps.moderation.models.change import Change
from apps.moderation.models.moderated_model.manager import (
    ModeratedModelManager,
    SearchableModeratedModelManager,
)
from apps.search.models.searchable_model import SearchableModel

if TYPE_CHECKING:
    from django.db.models.fields import Field


class ModeratedModel(models.Model):
    """Base class for models of which instances must be moderated."""

    changes = GenericRelation(to='moderation.Change')

    # This field is used to determine whether model instances should be visible to users.
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
    )

    objects = ModeratedModelManager()

    class Meta:
        abstract = True

    class Moderation:
        excluded_fields = ['cache', 'date_string']

    @property
    def change_in_progress(self) -> Optional['Change']:
        return (
            self.changes.filter(moderation_status=ModerationStatus.PENDING).first()
            if self.has_change_in_progress
            else None
        )

    @property
    def has_change_in_progress(self) -> bool:
        try:
            return self.changes.filter(moderation_status=ModerationStatus.PENDING).exists()
        except Exception as err:
            logging.error(err)
            return False

    def get_moderated_fields(self) -> list[dict]:
        """
        Return a serialized list of the model's moderated fields.

        This can be used to construct forms intelligently in front-end code.
        """
        fields = []
        field: 'Field'
        for field in self._meta.get_fields():
            if field.name in self.Moderation.excluded_fields:
                continue
            verbose_name = getattr(field, 'verbose_name', None)  # default to None
            editable = getattr(field, 'editable', True)  # default to True
            if not verbose_name or not editable:  # temporary heuristic -- TODO
                continue
            print(field.__dict__)
            fields.append(
                {
                    'name': field.name,
                    'verbose_name': verbose_name,
                    'editable': editable,
                    'choices': getattr(field, 'choices', None),
                    'help_text': getattr(field, 'help_text', None),
                    'type': field.__class__.__name__,
                }
            )
        return fields


class SearchableModeratedModel(SearchableModel, ModeratedModel):
    """Base class for moderated models of which users can search for instances."""

    objects = SearchableModeratedModelManager()

    class Meta:
        abstract = True
