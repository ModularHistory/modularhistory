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


class ParentlessCategoryFactory(ModeratedModelFactory):
    class Meta:
        model = models.Category

    name = factory.Faker('sentence', nb_words=3)
    part_of_speech = fuzzy.FuzzyChoice(models.PARTS_OF_SPEECH, getter=lambda c: c[0])
    aliases = factory.List([factory.Faker('sentence', nb_words=2) for _ in range(2)])
    weight = fuzzy.FuzzyInteger(0, 10)


class CategoryFactory(ParentlessCategoryFactory):
    class Meta:
        model = models.Category

    parent = factory.SubFactory(ParentlessCategoryFactory)
