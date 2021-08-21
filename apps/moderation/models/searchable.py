from typing import Type


from apps.moderation.models.moderated_model.manager import ModeratedModelManager
from apps.moderation.models.moderated_model.model import ModeratedModel
from apps.search.models.searchable_model import SearchableModel
from core.models.manager import SearchableManager


class SearchableModeratedModelManager(ModeratedModelManager, SearchableManager):
    """Manager for moderated models of which users can search for instances."""

    model: Type['SearchableModeratedModel']


class SearchableModeratedModel(ModeratedModel, SearchableModel):
    """Base class for moderated models of which users can search for instances."""

    objects = SearchableModeratedModelManager()

    class Meta:
        abstract = True
