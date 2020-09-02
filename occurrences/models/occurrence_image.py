# type: ignore
# TODO: remove above line after fixing typechecking
from django.db import models
from django.db.models import CASCADE
from django.utils.safestring import mark_safe

from history.models import Model
from images.models import Image


class OccurrenceImage(Model):
    """TODO: add docstring."""

    occurrence = models.ForeignKey(
        'occurrences.Occurrence', related_name='occurrence_images',
        on_delete=CASCADE
    )
    image = models.ForeignKey(Image, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Set to 0 if the image is positioned manually.'
    )

    class Meta:
        unique_together = ['occurrence', 'image']
        ordering = ['position', 'image']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return mark_safe(f'{self.position}: {self.image.caption}')

    @property
    def is_positioned(self) -> bool:
        """TODO: write docstring."""
        return f'image: {self.image.pk}' in self.occurrence.description.raw_value

    @property
    def image_pk(self) -> str:
        """TODO: write docstring."""
        return self.image.pk

    @property
    def key(self) -> str:
        """TODO: write docstring."""
        return self.image.key
