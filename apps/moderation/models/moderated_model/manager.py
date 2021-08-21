from typing import TYPE_CHECKING, Any, Optional, Type

from core.models.soft_deletable.managers import SoftDeletableManager
from core.models.soft_deletable.queryset import SoftDeletableQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class ModeratedQuerySet(SoftDeletableQuerySet):
    pass


class ModeratedManager(SoftDeletableManager):
    """Manager for moderated models."""

    model: Type['ModeratedModel']
    queryset_cls = ModeratedQuerySet
    exclude_unverified = True

    def get_queryset(self) -> ModeratedQuerySet:
        queryset = super().get_queryset()
        if self.exclude_unverified:
            return queryset.filter(verified=True)
        return queryset

    def create(self, *args, **kwargs) -> 'ModeratedModel':
        kwargs['verified'] = kwargs.get('verified', False)
        object: 'ModeratedModel' = super().create(*args, **kwargs)
        object.save_change()
        return object

    def get_or_create(
        self,
        defaults: Optional[dict[str, Any]],
        **kwargs,
    ) -> tuple['ModeratedModel', bool]:
        object: 'ModeratedModel'
        object, created = super().get_or_create(defaults=defaults, **kwargs)
        if created:
            object.save_change()
        return object, created
