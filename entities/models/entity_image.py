from typing import TYPE_CHECKING

from django.db.models import ForeignKey, CASCADE

from modularhistory.models import (
    Model
)
from images.models import Image

if TYPE_CHECKING:
    pass

NAME_MAX_LENGTH: int = 100

TRUNCATED_DESCRIPTION_LENGTH: int = 1200


class EntityImage(Model):
    """TODO: add docstring."""

    entity = ForeignKey('entities.Entity', related_name='entity_images', on_delete=CASCADE)
    image = ForeignKey(Image, related_name='image_entities', on_delete=CASCADE)

    class Meta:
        unique_together = ['entity', 'image']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return f'{self.image} ({self.image.id}) --> {self.entity} ({self.entity.id})'
