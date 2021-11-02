import base64

import factory.fuzzy
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory

from apps.images import models


def fake_image():
    image = base64.b64decode(
        b'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
    )

    return SimpleUploadedFile('test.png', image, content_type='image/png')


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = models.Image

    image = fake_image()
    width = factory.fuzzy.FuzzyInteger(500, 1000)
    height = factory.fuzzy.FuzzyInteger(500, 1000)
    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    caption = factory.Faker('sentence', nb_words=10)
    description = factory.Faker('text')
    provider = factory.Faker('company')
    image_type = factory.fuzzy.FuzzyChoice(models.IMAGE_TYPES, getter=lambda c: c[0])
