"""Occurrence images."""

from django.db import models
from django.db.models import CASCADE
from django.utils.html import format_html

from modularhistory.models import Model


class OccurrenceImage(Model):
    """An association of an image with an occurrence."""

    occurrence = models.ForeignKey(
        'occurrences.Occurrence', related_name='occurrence_images', on_delete=CASCADE
    )
    image = models.ForeignKey('images.Image', on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text='Set to 0 if the image is positioned manually.'
    )

    class Meta:
        unique_together = ['occurrence', 'image']
        ordering = ['position', 'image']

    def __str__(self) -> str:
        """Return the string representation of the occurrence–image relation."""
        return format_html(f'{self.position}: {self.image.caption}')

    @property
    def is_positioned(self) -> bool:
        """Return True if the image is manually positioned within the occurrence's description."""
        return f'image: {self.image.pk}' in self.occurrence.description.raw_value

    @property
    def image_pk(self) -> str:
        """Return the primary key of the image."""
        return self.image.pk

    @property
    def key(self) -> str:
        """Return the key of the image."""
        return f'{self.image.key}'
