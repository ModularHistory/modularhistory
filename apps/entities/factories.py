import factory
from factory import fuzzy

from apps.entities import models
from apps.moderation.factories import ModeratedModelFactory
from core.factories import UniqueFaker


class EntityFactory(ModeratedModelFactory):
    class Meta:
        model = models.Entity

    type = fuzzy.FuzzyChoice(
        [key for key in models.Entity._typedmodels_registry.keys() if key != 'entities.deity']
    )
    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    name = UniqueFaker('name')
    unabbreviated_name = UniqueFaker('name')
    aliases = factory.List([UniqueFaker('name') for _ in range(3)])
    birth_date = factory.Faker('historic_datetime')
    death_date = factory.Faker('historic_datetime')
    description = factory.Faker('text')
