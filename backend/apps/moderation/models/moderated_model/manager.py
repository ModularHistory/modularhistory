from typing import TYPE_CHECKING

from django.conf import settings

from core.models.soft_deletable.managers import SoftDeletableManager
from core.models.soft_deletable.queryset import SoftDeletableQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class ModeratedQuerySet(SoftDeletableQuerySet):
    """Default queryset for the ModeratedManager.
    Calling obj.delete/undelete is inefficient but allows moderated deletes.
    """

    def delete(self):
        """Override bulk delete behavior."""
        assert self.query.can_filter(), 'Cannot use "limit" or "offset" with delete.'
        obj: 'ModeratedModel'
        for obj in self.all():
            obj.delete()
        self._result_cache = None

    delete.alters_data = True

    def undelete(self):
        """Undelete soft-deleted instances."""
        assert self.query.can_filter(), 'Cannot use "limit" or "offset" with undelete.'
        obj: 'ModeratedModel'
        for obj in self.all():
            obj.undelete()
        self._result_cache = None

    undelete.alters_data = True


class ModeratedManager(SoftDeletableManager):
    """Manager for moderated models."""

    model: type['ModeratedModel']
    queryset_cls = ModeratedQuerySet
    exclude_unverified = settings.TESTING  # TODO: change to True

    def get_queryset(self) -> ModeratedQuerySet:
        """Return the default queryset to be used by the manager."""
        queryset = super().get_queryset()
        if self.exclude_unverified:
            return queryset.filter(verified=True)
        return queryset

    def create(self, *args, **kwargs) -> 'ModeratedModel':
        """Create and return a model instance."""
        kwargs['verified'] = kwargs.get('verified', False)
        object: 'ModeratedModel' = super().create(*args, **kwargs)
        return object

    def get_or_create(self, **kwargs) -> tuple['ModeratedModel', bool]:
        """Get or create the model instance with the specified kwargs and return it."""
        object: 'ModeratedModel'
        object, created = super().get_or_create(**kwargs)
        return object, created
