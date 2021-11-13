import base64

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import fuzzy
from factory.django import ImageField

from apps.images import models
from apps.moderation.factories import ModeratedModelFactory


def generate_temporary_image() -> SimpleUploadedFile:
    file = SimpleUploadedFile(
        'test.png',
        content=base64.b64decode(
            b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
        ),
        content_type='image/png',
    )
    file.seek(0)
    return file


class ImageFactory(ModeratedModelFactory):
    class Meta:
        model = models.Image

    image = ImageField(from_func=generate_temporary_image)
    width = fuzzy.FuzzyInteger(500, 1000)
    height = fuzzy.FuzzyInteger(500, 1000)
    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    caption = factory.Faker('sentence', nb_words=10)
    description = factory.Faker('text')
    provider = factory.Faker('company')
    image_type = fuzzy.FuzzyChoice(models.IMAGE_TYPES, getter=lambda c: c[0])
