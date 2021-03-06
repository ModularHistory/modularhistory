"""Occurrence images."""

from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from modularhistory.models.positioned_relation import PositionedRelation


class OccurrenceImage(PositionedRelation):
    """An association of an image with an occurrence."""

    occurrence = models.ForeignKey(
        to='occurrences.Occurrence',
        related_name='image_relations',
        on_delete=models.CASCADE,
        verbose_name=_('occurrence'),
    )
    image = models.ForeignKey(
        to='images.Image',
        related_name='occurrence_relations',
        on_delete=models.PROTECT,
        verbose_name=_('image'),
    )
    is_positioned = models.BooleanField(blank=True, default=False)

    class Meta:
        """
        Meta options for OccurrenceImage.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        unique_together = ['occurrence', 'image']
        ordering = ['position']

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
