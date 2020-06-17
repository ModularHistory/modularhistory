from django.db import models
from django.db.models import CASCADE
from django.utils.safestring import mark_safe

from history.models import Model
from images.models import Image


class OccurrenceImage(Model):
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

    def __str__(self):
        return mark_safe(f'{self.position}: {self.image.caption}')

    @property
    def is_positioned(self) -> bool:
        return f'image: {self.image.pk}' in self.occurrence.description.raw_value

    @property
    def image_pk(self) -> str:
        return self.image.pk

    @property
    def key(self) -> str:
        return self.image.key