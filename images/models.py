from typing import Optional
from django.core.exceptions import ValidationError

from django.db import models
from django.utils.safestring import SafeText, mark_safe
# from polymorphic.models import PolymorphicModel
from taggit.models import TaggedItemBase
import pafy
from history.fields.file_field import upload_to
from history.fields.historic_datetime_field import HistoricDateTimeField
from history.fields.html_field import HTMLField
from history.models import TypedModel, Model, TaggableModel, SearchableMixin
from .manager import Manager

image_types = (
    ('image', 'Image'),
    ('photo', 'Photo'),
    ('illustration', 'Illustration'),
    ('painting', 'Painting'),
    ('portrait', 'Portrait'),
    ('diagram', 'Diagram'),
    ('reconstruction', 'Reconstruction'),
    ('photomontage', 'Photomontage'),
    ('model', 'Model'),
)


class Image(TypedModel, TaggableModel, SearchableMixin):
    """An image"""
    objects: Manager = Manager()

    image = models.ImageField(
        upload_to=upload_to('images/'),
        height_field='height', width_field='width',
        null=True  # but not blank=True
    )
    caption = HTMLField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    provider = models.CharField(max_length=200, null=True, blank=True)
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    date = HistoricDateTimeField(null=True, blank=True)
    type = models.CharField(max_length=14, choices=image_types, default='image')

    searchable_fields = ['caption', 'description', 'provider']

    class Meta:
        unique_together = ['image', 'caption']
        ordering = ['date']

    def __str__(self):
        return self.caption.text if self.caption else self.image.name

    @property
    def admin_image_element(self) -> SafeText:
        height = 150
        width = height * self.aspect_ratio
        return mark_safe(f'<img src="{self.image.url}" width="{width}px" height="{height}px" />')

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    @property
    def provider_string(self) -> Optional[str]:
        if (not self.provider) or self.provider in self.caption.text:
            return None
        phrase = 'provided'
        if self.type == 'painting':
            phrase = None
        string = f'{self.type.title()}{(" " + phrase) if phrase else ""} by {self.provider}'
        return string

    @property
    def thumbnail(self) -> SafeText:
        height = 100
        width = height * self.aspect_ratio
        return mark_safe(f'<img class="thumbnail" src="{self.image.url}" width="{width}px" height="{height}px" />')

    def natural_key(self):
        return self.image,


class Photo(Image):
    """A photo"""
    pass


class Illustration(Image):
    """An illustration"""
    pass


class Video(Image):
    """A video"""
    title = models.CharField(max_length=200, null=True)
    link = models.URLField(null=True)
    embed_code = models.CharField(max_length=200, null=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    def clean(self):
        if not self.link:
            raise ValidationError('Video needs a link.')
        video = pafy.new(self.link)
        if not self.title:
            self.title = video.title
        if not self.duration:
            self.duration = video.duration

