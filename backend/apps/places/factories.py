import factory
from factory import fuzzy

from apps.moderation.factories import ModeratedModelFactory
from apps.places import models
from core.factories import UniqueFaker


class PlaceFactory(ModeratedModelFactory):
    class Meta:
        model = models.Place

    type = fuzzy.FuzzyChoice(models.Place._typedmodels_registry.keys())
    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    name = UniqueFaker('city')
    preposition = fuzzy.FuzzyChoice(models.base.PREPOSITION_CHOICES, getter=lambda c: c[0])
