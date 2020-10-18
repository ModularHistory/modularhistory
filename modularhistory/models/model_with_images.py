"""Classes for models with related entities."""

from typing import Any, Optional, TYPE_CHECKING

from modularhistory.models.model import Model

if TYPE_CHECKING:
    from images.models import Image


class ModelWithImages(Model):
    """
    A model that has one or more associated images.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    images: Any

    class Meta:
        abstract = True

    @property
    def primary_image(self) -> Optional['Image']:
        """Return the image to represent the model instance by default."""
        return self.images.first() if self.images.exists() else None
