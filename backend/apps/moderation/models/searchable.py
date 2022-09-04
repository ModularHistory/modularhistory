from apps.moderation.models.moderated_model.manager import ModeratedManager, ModeratedQuerySet
from apps.moderation.models.moderated_model.model import ModeratedModel
from apps.search.models.searchable_model import SearchableModel
from core.models.manager import SearchableManager, SearchableQuerySet


class SearchableModeratedQuerySet(ModeratedQuerySet, SearchableQuerySet):
    """Lazy db lookup for searchable moderated models."""


class SearchableModeratedManager(ModeratedManager, SearchableManager):
    """Manager for moderated models of which users can search for instances."""

    model: type['SearchableModeratedModel']
    queryset_cls = SearchableModeratedQuerySet


class SearchableModeratedModel(ModeratedModel, SearchableModel):
    """Base class for moderated models of which users can search for instances."""

    objects = SearchableModeratedManager()

    class Meta:
        abstract = True

    def pre_save(self):
        SearchableModel.pre_save(self)
        ModeratedModel.pre_save(self)

    def post_save(self):
        SearchableModel.post_save(self)
        ModeratedModel.post_save(self)
