"""Occurrence images."""

from django.db import models
from django.db.models import CASCADE
from django.utils.html import format_html

from modularhistory.models import Model


class OccurrenceImage(Model):
    """An association of an image with an occurrence."""

    occurrence = models.ForeignKey(
        'occurrences.Occurrence', related_name='image_relations', on_delete=CASCADE
    )
    image = models.ForeignKey(
        'images.Image', related_name='occurrence_relations', on_delete=models.PROTECT
    )
    is_positioned = models.BooleanField(blank=True, default=False)
    position = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text='Set to 0 if the image is positioned manually.'
    )

    class Meta:
        unique_together = ['occurrence', 'image']
        ordering = ['position', 'image']

    def __str__(self) -> str:
        """Return the string representation of the occurrence–image relation."""
        return format_html(f'{self.position}: {self.image.caption}')

    def save(self, *args, **kwargs):
        """Save the occurrence–image association."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Prepare the occurrence–image association to be saved."""
        try:
            is_positioned = (
                f'image: {self.image.pk}' in self.occurrence.description.raw_value
            )
        except AttributeError:
            is_positioned = False
        self.is_positioned = is_positioned

    @property
    def image_pk(self) -> str:
        """Return the primary key of the image."""
        return self.image.pk

    @property
    def key(self) -> str:
        """Return the key of the image."""
        return f'{self.image.key}'
