import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.places import models


class PlaceFactory(DjangoModelFactory):
    class Meta:
        model = models.Place

    type = factory.fuzzy.FuzzyChoice(models.Place.typedmodels_registry.keys())
    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    name = factory.Faker('city')
    preposition = factory.fuzzy.FuzzyChoice(
        models.base.PREPOSITION_CHOICES, getter=lambda c: c[0]
    )
