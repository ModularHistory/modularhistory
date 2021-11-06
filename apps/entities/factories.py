import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from apps.entities import models


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = models.Entity

    type = fuzzy.FuzzyChoice(
        [key for key in models.Entity._typedmodels_registry.keys() if key != 'entities.deity']
    )
    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    name = factory.Faker('name')
    unabbreviated_name = factory.Faker('name')
    aliases = factory.List([factory.Faker('name') for _ in range(3)])
    birth_date = factory.Faker('historic_datetime')
    death_date = factory.Faker('historic_datetime')
    description = factory.Faker('text')
