import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.images import models


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = models.Image

    width = factory.fuzzy.FuzzyInteger(500, 1000)
    height = factory.fuzzy.FuzzyInteger(500, 1000)
    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    caption = factory.Faker('sentence', nb_words=10)
    description = factory.Faker('text')
    provider = factory.Faker('company')
    image_type = factory.fuzzy.FuzzyChoice(models.IMAGE_TYPES, getter=lambda c: c[0])
