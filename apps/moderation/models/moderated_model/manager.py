from typing import TYPE_CHECKING, Type

from django.db.models.manager import Manager

from core.models.manager import SearchableManager

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import (
        ModeratedModel,
        SearchableModeratedModel,
    )


class ModeratedModelManager(Manager):
    """Manager for moderated models."""

    model: Type['ModeratedModel']


class SearchableModeratedModelManager(SearchableManager, ModeratedModelManager):
    """Manager for moderated models of which users can search for instances."""

    model: Type['SearchableModeratedModel']
