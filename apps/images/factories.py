import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import fuzzy
from factory.django import DjangoModelFactory, ImageField

from apps.images import models


def fake_image():
    return SimpleUploadedFile(
        'test.png',
        content=ImageField()._make_data({'width': 1024, 'height': 768}),
        content_type='image/png',
    )


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = models.Image

    image = ImageField(from_func=fake_image)
    width = fuzzy.FuzzyInteger(500, 1000)
    height = fuzzy.FuzzyInteger(500, 1000)
    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    caption = factory.Faker('sentence', nb_words=10)
    description = factory.Faker('text')
    provider = factory.Faker('company')
    image_type = fuzzy.FuzzyChoice(models.IMAGE_TYPES, getter=lambda c: c[0])
