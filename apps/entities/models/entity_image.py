from django.db import models

from core.models import Model

NAME_MAX_LENGTH: int = 100

TRUNCATED_DESCRIPTION_LENGTH: int = 1200


class EntityImage(Model):
    """An association of an image with an entity."""

    entity = models.ForeignKey(
        'entities.Entity', related_name='image_relations', on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        'images.Image', related_name='entity_relations', on_delete=models.CASCADE
    )

    class Meta:
        """
        Meta options for the EntityImage model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        unique_together = ['entity', 'image']

    def __str__(self) -> str:
        """Return the string representation of the entity–image association."""
        return f'{self.image} ({self.image.id}) --> {self.entity} ({self.entity.id})'
