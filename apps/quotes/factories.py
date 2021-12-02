import factory

from apps.moderation.factories import ModeratedModelFactory
from apps.quotes import models


class QuoteFactory(ModeratedModelFactory):
    class Meta:
        model = models.Quote

    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    text = factory.Faker('text')
    bite = factory.Faker('text')
    date = factory.Faker('historic_datetime')
