# https://github.com/craigds/django-typed-models

from typedmodels.models import TypedModel as BasedTypedModel
from typedmodels.models import TypedModelManager as BaseTypedModelManager
from typedmodels.models import TypedModelMetaclass

from core.models import ExtendedModel


class TypedModelManager(BaseTypedModelManager):
    """Manager for typed models."""


class TypedModel(BasedTypedModel, ExtendedModel, metaclass=TypedModelMetaclass):
    """Base model for models implementing single-table inheritance via `type`."""

    _typedmodels_registry: dict

    class Meta:
        abstract = True

    objects = TypedModelManager()

    def pre_save(self):
        super().pre_save()
        if not getattr(self, '_typedmodels_type', None):
            raise RuntimeError(f'Untyped {self.__class__.__name__} cannot be saved.')

    def save(self, *args, **kwargs):
        ExtendedModel.save(self, *args, **kwargs)
