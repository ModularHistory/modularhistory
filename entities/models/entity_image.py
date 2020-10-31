from django.db.models import CASCADE, ForeignKey

from modularhistory.models import Model

NAME_MAX_LENGTH: int = 100

TRUNCATED_DESCRIPTION_LENGTH: int = 1200


class EntityImage(Model):
    """An association of an image with an entity."""

    entity = ForeignKey(
        'entities.Entity', related_name='image_relations', on_delete=CASCADE
    )
    image = ForeignKey(
        'images.Image', related_name='entity_relations', on_delete=CASCADE
    )

    class Meta:
        unique_together = ['entity', 'image']

    def __str__(self) -> str:
        """Return the string representation of the entity–image association."""
        return f'{self.image} ({self.image.id}) --> {self.entity} ({self.entity.id})'
