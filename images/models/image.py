import re
from sys import stderr
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer
from image_cropping import ImageRatioField

from images.manager import ImageManager
from images.models.media_model import MediaModel
from modularhistory.fields.file_field import upload_to

FLOAT_UPPER_WIDTH_LIMIT: int = 300
CENTER_UPPER_WIDTH_LIMIT: int = 500

# group 1: image pk
# group 2: ignore (appendage)
# group 3: image HTML
ADMIN_PLACEHOLDER_REGEX = r'<<\ ?image:\ ?([\d\w-]+?)(:\ ?(?!>>)([\s\S]+?))?\ ?>>'

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


# TODO
# STORAGE_OPTIONS = (
#     'mega',
# )


class Image(MediaModel):
    """An image."""

    image = models.ImageField(
        upload_to=upload_to('images/'),
        height_field='height', width_field='width',
        null=True
    )
    image_type = models.CharField(
        max_length=TYPE_NAME_MAX_LENGTH,
        choices=IMAGE_TYPES,
        default='image'
    )
    links = JSONField(default=dict, blank=True)
    width = models.PositiveSmallIntegerField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    # https://github.com/jonasundderwolf/django-image-cropping
    cropping = ImageRatioField(
        'image',
        free_crop=True,
        allow_fullsize=True,
        help_text='Not yet fully implemented.'
    )

    class Meta:
        unique_together = ['image', 'caption']
        ordering = ['date']

    searchable_fields = ['caption', 'description', 'provider']
    objects: ImageManager = ImageManager()  # type: ignore
    admin_placeholder_regex = re.compile(ADMIN_PLACEHOLDER_REGEX)

    def __str__(self) -> str:
        """Returns the string representation of the image."""
        return self.caption.text if self.caption else self.image.name

    @property
    def admin_image_element(self) -> SafeString:
        """Returns an image element to be displayed in the image admin."""
        height = 150
        max_width = 300
        width = height * self.aspect_ratio
        if width > max_width:
            width, height = max_width, int(max_width / self.aspect_ratio)
        return format_html(f'<img src="{self.image.url}" width="{width}px" height="{height}px" />')

    @property
    def aspect_ratio(self) -> float:
        """Returns the image's aspect ratio as a float."""
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
                'size': (self.width, self.height),
                'box': self.cropping,
                'crop': True,
                'detail': True,
            }).url
        except KeyError as error:
            # TODO: Send email to admins about the error. Figure out why this happens.
            print(f'KeyError: {error}', file=stderr)
        except OSError as error:
            # TODO: Send email to admins about the error. Figure out why this happens.
            print(f'OSError: {error}', file=stderr)
        return None

    @property
    def provider_string(self) -> Optional[str]:
        """Image credit string (e.g., "Image provided by NASA") displayed in caption."""
        if (not self.provider) or self.provider in self.caption.text:
            return None
        provision_phrase = 'provided'
        if self.image_type == 'painting':
            provision_phrase = None
        components = [
            f'{self.image_type.title()}',
            provision_phrase,
            f'by {self.provider}'
        ]
        return ' '.join([component for component in components if component])

    @property
    def src_url(self) -> str:
        """Returns the URL to be used for the `src` attribute in HTML."""
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
        multiplier = 1.2
        return 'center 10%' if self.height > (self.width * multiplier) else 'center'

    def clean(self):
        """Prepares the image to be saved."""
        super().clean()
        if not self.caption:
            raise ValidationError('Image needs a caption.')
        if self.caption and Image.objects.filter(image=self.image, caption=self.caption).exists():
            raise ValidationError(f'{self.image} with caption=`{self.caption}` already exists.')
        # # TODO
        # if mega and not len(self.links):
        #     pass
        #     # mega_client = mega.login(MEGA_USERNAME, MEGA_PASSWORD)
        #     # mega_client.upload(self.image.url)
        #     # input('continue?')

    @classmethod
    def get_object_html(cls, match: re.Match, use_preretrieved_html: bool = False) -> str:
        """Return the obj's HTML based on a placeholder in the admin."""
        if not re.match(ADMIN_PLACEHOLDER_REGEX, match.group(0)):
            raise ValueError(f'{match} does not match {ADMIN_PLACEHOLDER_REGEX}')

        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(3)
            if preretrieved_html:
                return preretrieved_html.strip()

        key = match.group(1).strip()
        # Update key if necessary
        try:
            image = cls.objects.get(pk=key)
        except ValueError as error:  # legacy key
            image = cls.objects.get(key=key)
            print(f'image {key} --> {image.pk}: {error}', file=stderr)
            # img_placeholder = img_placeholder.replace(key, str(image.pk))  # TODO
        image_html = render_to_string(
            'images/_card.html',
            context={'image': image, 'obj': image}
        )
        if image.width < FLOAT_UPPER_WIDTH_LIMIT:
            image_html = f'<div class="float-right pull-right">{image_html}</div>'
        if image.width < CENTER_UPPER_WIDTH_LIMIT:
            image_html = f'<div style="text-align: center">{image_html}</div>'
        return image_html

    @classmethod
    def get_updated_placeholder(cls, match: re.Match) -> str:
        """Return an up-to-date placeholder for an image included in an HTML field."""
        placeholder = match.group(0)
        appendage = match.group(2)
        updated_appendage = f': {cls.get_object_html(match)}'
        if appendage:
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            updated_placeholder = (
                f'{placeholder.replace(" >>", "").replace(">>", "")}'
                f'{updated_appendage} >>'
            )
        return updated_placeholder.replace('\n\n\n', '\n').replace('\n\n', '\n')
