from typing import Type

from apps.moderation.models.moderated_model.manager import ModeratedManager, ModeratedQuerySet
from apps.moderation.models.moderated_model.model import ModeratedModel
from apps.search.models.searchable_model import SearchableModel
from core.models.manager import SearchableManager, SearchableQuerySet


class SearchableModeratedQuerySet(ModeratedQuerySet, SearchableQuerySet):
    """Lazy db lookup for searchable moderated models."""


class SearchableModeratedManager(ModeratedManager, SearchableManager):
    """Manager for moderated models of which users can search for instances."""

    model: Type['SearchableModeratedModel']
    queryset_cls = SearchableModeratedQuerySet


class SearchableModeratedModel(ModeratedModel, SearchableModel):
    """Base class for moderated models of which users can search for instances."""

    objects = SearchableModeratedManager()

    class Meta:
        abstract = True

    def pre_save(self):
        super(SearchableModel, self).pre_save()
        super(ModeratedModel, self).pre_save()

    def post_save(self):
        super(SearchableModel, self).post_save()
        super(ModeratedModel, self).post_save()
