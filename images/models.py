from typing import Optional

import pafy
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import SafeText, mark_safe
from image_cropping import ImageRatioField
from easy_thumbnails.files import get_thumbnailer
from history.fields import HTMLField
from history.fields.file_field import upload_to
from history.models import Model, DatedModel, TaggableModel, SearchableMixin
from .manager import Manager as ImageManager


class MediaModel(TaggableModel, DatedModel, SearchableMixin):
    caption = HTMLField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    provider = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True


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


class Image(MediaModel):
    """An image"""
    image = models.ImageField(
        upload_to=upload_to('images/'),
        height_field='height', width_field='width',
        null=True
    )
    type = models.CharField(max_length=14, choices=image_types, default='image')
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    # https://github.com/jonasundderwolf/django-image-cropping
    cropping = ImageRatioField('image', free_crop=True, allow_fullsize=True,
                                    help_text='Not yet fully implemented.')

    class Meta:
        unique_together = ['image', 'caption']
        ordering = ['date']

    searchable_fields = ['caption', 'description', 'provider']
    objects: ImageManager = ImageManager()

    def __str__(self):
        return self.caption.text if self.caption else self.image.name

    @property
    def admin_image_element(self) -> SafeText:
        height = 150
        max_width = 300
        width = height * self.aspect_ratio
        if width > max_width:
            width, height = max_width, max_width / self.aspect_ratio
        return mark_safe(f'<img src="{self.image.url}" width="{width}px" height="{height}px" />')

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    @property
    def cropped_image_url(self) -> Optional[str]:
        """
        URL for the cropped version of the image.

        Reference:
        https://github.com/jonasundderwolf/django-image-cropping#user-content-easy-thumbnails
        """
        if not self.cropping:
            return None
        try:
            return get_thumbnailer(self.image).get_thumbnail({
                'box': self.cropping,
                'crop': True,
                'detail': True,
            }).url
        except KeyError as e:
            print(f'>>> {e}')  # TODO: Send email to admins about the error. Figure out why this happens.
            return None

    @property
    def provider_string(self) -> Optional[str]:
        """
        Image credit string (e.g., "Image provided by NASA") displayed in the caption.
        """
        if (not self.provider) or self.provider in self.caption.text:
            return None
        phrase = 'provided'
        if self.type == 'painting':
            phrase = None
        string = f'{self.type.title()}{(" " + phrase) if phrase else ""} by {self.provider}'
        return string

    @property
    def src_url(self) -> str:
        return self.cropped_image_url or self.image.url

    @property
    def bg_img_position(self) -> str:
        """
        CSS `background-position` value (e.g., "center" or "top center")
        to use when displaying the image as the background of a div.

        Reference: https://www.w3schools.com/cssref/pr_background-position.asp

        This is used to position the background images of the SERP cards.
        """
        # If the image is tall and narrow, it's like to be of a person or figurine;
        # try to to avoid cutting off heads.
        return 'center' if not self.height > (1.2 * self.width) else 'center 10%'

    def clean(self):
        super().clean()
        if not self.caption:
            raise ValidationError('Image needs a caption.')


class Video(MediaModel):
    """A video"""
    title = models.CharField(max_length=200, null=True)
    link = models.URLField(null=True, unique=True)
    embed_code = models.CharField(max_length=200, null=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['title', 'link']

    def clean(self):
        if not self.link:
            raise ValidationError('Video needs a link.')
        try:
            video = pafy.new(self.link)
            if not self.title:
                self.title = video.title
            if not self.duration:
                self.duration = video.duration
        except Exception as e:  # TODO: Enable saving other kinds of videos
            raise Exception(f'Error: {e} \n Note: Non-YouTube videos are not yet supported.')

