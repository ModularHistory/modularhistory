import factory
from factory.django import DjangoModelFactory

from apps.quotes import models


class QuoteFactory(DjangoModelFactory):
    class Meta:
        model = models.Quote

    title = factory.Faker('sentence', nb_words=10)
    text = factory.Faker('text')
    date = factory.Faker('historic_datetime')
