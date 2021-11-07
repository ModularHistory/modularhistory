import base64

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import fuzzy
from factory.django import DjangoModelFactory, ImageField

from apps.images import models


def generate_temporary_image():
    file = SimpleUploadedFile(
        'test.png',
        content=base64.b64decode(
            b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
        ),
        content_type='image/png',
    )
    return file


class ImageFactory(DjangoModelFactory):
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
