import logging
from typing import Match, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from image_cropping import ImageRatioField
from rest_framework.serializers import Serializer

from apps.images.models.media_model import MediaModel
from apps.topics.models.taggable import AbstractTopicRelation, TagsField
from core.fields.file_field import upload_to
from core.fields.html_field import OBJECT_PLACEHOLDER_REGEX, TYPE_GROUP, PlaceholderGroups
from core.fields.json_field import JSONField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.utils.string import components_to_string

FLOAT_UPPER_WIDTH_LIMIT: int = 300
CENTER_UPPER_WIDTH_LIMIT: int = 500

IMAGE_TYPES = (
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

TYPE_NAME_MAX_LENGTH = 14

IMAGE_KEY = IMAGE_FIELD_NAME = 'image'

image_placeholder_regex: str = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>image)'  # noqa: WPS360
)
logging.debug(f'Image placeholder pattern: {image_placeholder_regex}')


def get_image_fk(related_name: str) -> ManyToManyForeignKey:
    """Return a foreign key field referencing a image."""
    return ManyToManyForeignKey(
        to='images.Image',
        related_name=related_name,
        verbose_name='image',
    )


class TopicRelation(AbstractTopicRelation):
    """A relationship between a image and a topic."""

    content_object = get_image_fk(related_name='topic_relations')


class Image(MediaModel):
    """An image."""

    image = models.ImageField(
        verbose_name=_('image'),
        upload_to=upload_to('images/'),
        height_field='height',
        width_field='width',
        null=True,
    )
    image_type = models.CharField(
        verbose_name=_('image type'),
        max_length=TYPE_NAME_MAX_LENGTH,
        choices=IMAGE_TYPES,
        default=IMAGE_TYPES[0][0],
    )
    urls = JSONField(default=dict, blank=True)
    width = models.PositiveSmallIntegerField(verbose_name=_('width'), blank=True)
    height = models.PositiveSmallIntegerField(verbose_name=_('height'), blank=True)
    # https://github.com/jonasundderwolf/django-image-cropping
    cropping = ImageRatioField(
        image_field=IMAGE_FIELD_NAME,
        free_crop=True,
        allow_fullsize=True,
        verbose_name=_('cropping'),
        help_text='Not yet fully implemented.',
    )

    alt_text = models.CharField(
        verbose_name=_('alt text'),
        max_length=255,
        blank=True,
    )

    tags = TagsField(through=TopicRelation)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        unique_together = [IMAGE_FIELD_NAME, 'caption']
        ordering = ['date']

    placeholder_regex = image_placeholder_regex
    searchable_fields = [
        'caption',
        'description',
        'provider',
    ]

    @classmethod
    def get_serializer(self) -> type[Serializer]:
        """Return the serializer for the entity."""
        from apps.images.api.serializers import ImageSerializer

        return ImageSerializer

    def __str__(self) -> str:
        """Return the string representation of the image."""
        return self.caption or self.image.name

    def clean(self):
        super().clean()
        image_is_duplicated = (
            self.caption
            and Image.objects.filter(image=self.image, caption=self.caption)
            .exclude(pk=self.pk)
            .exists()
        )
        if image_is_duplicated:
            raise ValidationError(
                f'{self.image} with caption=`{self.caption}` already exists.'
            )

    @property
    def admin_image_element(self) -> SafeString:
        """Return an image element to be displayed in the image admin."""
        height = 150
        max_width = 300
        width = height * self.aspect_ratio
        if width > max_width:
            width, height = max_width, int(max_width / self.aspect_ratio)
        return format_html(
            f'<a target="_blank" href="/_admin/images/image/{self.pk}/change/">'
            f'<img src="{self.image.url}" width="{width}px" height="{height}px" />'
            '</a>'
        )

    @property
    def aspect_ratio(self) -> float:
        """Return the image's aspect ratio as a float."""
        return self.width / self.height  # type: ignore

    @property
    def cropped_image_url(self) -> Optional[str]:
        """
        URL for the cropped version of the image.

        Reference:
        https://github.com/jonasundderwolf/django-image-cropping#user-content-easy-thumbnails
        """
        enable_cropped_images = False
        if enable_cropped_images:
            try:
                if self.cropping:
                    thumbnail_params = {
                        'size': (self.width, self.height),
                        'box': self.cropping,
                        'crop': True,
                        'detail': True,
                    }
                    return get_thumbnailer(self.image).get_thumbnail(thumbnail_params).url
            except Exception as error:
                logging.error(
                    f'Attempt to retrieve cropped_image_url for image {self.pk} '
                    f'({self.image.file}, associated with {self}) resulted in '
                    f'{type(error)}: {error}'
                )
            return None
        return self.image.url

    @property
    def provider_string(self) -> str:
        """Image credit string (e.g., "Image provided by NASA") displayed in caption."""
        if (not self.provider) or self.provider in self.caption:
            return ''
        provision_phrase: Optional[str] = 'provided'
        if self.image_type == 'painting':
            provision_phrase = None
        components = [
            f'{self.image_type.title()}',
            provision_phrase,
            f'by {self.provider}',
        ]
        return components_to_string(components, delimiter=' ')

    @property
    def src_url(self) -> str:
        """Return the URL to be used for the `src` attribute in HTML."""
        return self.image.url  # TODO: self.cropped_image_url

    @property
    def bg_img_position(self) -> str:
        """
        Return the CSS `background-position` value (e.g., "center" or "top center").

        This value is used when displaying the image as the background of a div.
        Reference: https://www.w3schools.com/cssref/pr_background-position.asp
        This is used to position the background images of the SERP cards.
        """
        # If the image is tall and narrow, it's like to be of a person or figurine;
        # try to to avoid cutting off heads.
        multiplier = 1.2
        if self.width and self.height:
            if self.height > (self.width * multiplier):
                return 'center 10%'
        return 'center'

    @classmethod
    def get_object_html(cls, match: Match, use_preretrieved_html: bool = False) -> str:
        """Return the image's HTML based on a placeholder in the admin."""
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return str(preretrieved_html).strip()
        image = cls.objects.get(pk=match.group(PlaceholderGroups.PK))
        if isinstance(image, dict):
            width = image['width']
        elif isinstance(image, Image):
            width = image.width
        else:
            raise TypeError(f'k{image} is not an image or dictionary.')
        image_html = render_to_string('images/_card.html', context={IMAGE_KEY: image})
        if width < FLOAT_UPPER_WIDTH_LIMIT:
            image_html = f'<div class="float-right pull-right mx-3">{image_html}</div>'
        elif width < CENTER_UPPER_WIDTH_LIMIT:
            image_html = f'<div style="text-align: center">{image_html}</div>'
        image_html = image_html.strip()
        return image_html
