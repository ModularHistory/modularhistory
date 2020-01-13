from django.db import models
from django.db.models import ForeignKey, CASCADE
from django.utils.safestring import SafeText, mark_safe
# from polymorphic.models import PolymorphicModel
from taggit.models import TaggedItemBase

from history.fields import HTMLField, HistoricDateField
from history.models import TypedModel, Model, TaggableModel


# from tinymce.models import HTMLField


class Image(TypedModel, TaggableModel):
    """An image"""
    image = models.ImageField(upload_to='images', null=True)
    description = HTMLField(null=True, blank=True)
    provider = models.CharField(max_length=200, null=True, blank=True)
    max_width = models.PositiveSmallIntegerField(null=True, blank=True)
    date = HistoricDateField(null=True, blank=True)
    year = ForeignKey('occurrences.Year', null=True, blank=True, on_delete=CASCADE)

    searchable_fields = ['description', 'provider',]

    def __str__(self):
        return self.description.text if self.description else self.image.name

    @property
    def admin_image_element(self) -> SafeText:
        return mark_safe(f'<img src="{self.image.url}" height="150px" />')

    @property
    def thumbnail(self) -> SafeText:
        return mark_safe(f'<img class="thumbnail" src="{self.image.url}" width="100px" height="100px" '
                         f'style="float: left; margin-right: 0.5rem;" />')

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
    length = models.PositiveSmallIntegerField(null=True, blank=True)
