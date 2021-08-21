from typing import TYPE_CHECKING, Type

from core.models.soft_deletable.managers import SoftDeletableManager

if TYPE_CHECKING:
    from apps.moderation.models.moderated_model import ModeratedModel


class ModeratedModelManager(SoftDeletableManager):
    """Manager for moderated models."""

    model: Type['ModeratedModel']

    # def create(self, *args, **kwargs) -> 'ModeratedModel':
    #     kwargs['verified'] = False
    #     object = super().create(*args, **kwargs)
    #     Change.objects.create()
    #     return object
