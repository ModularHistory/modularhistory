import factory
from factory.django import DjangoModelFactory

from apps.quotes import models


class QuoteFactory(DjangoModelFactory):
    class Meta:
        model = models.Quote

    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    text = factory.Faker('text')
    bite = factory.Faker('text')
    date = factory.Faker('historic_datetime')
