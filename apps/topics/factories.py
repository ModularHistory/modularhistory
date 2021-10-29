import factory
from factory.django import DjangoModelFactory

from apps.topics import models


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = models.Topic

    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    name = factory.Faker('sentence', nb_words=1)
    aliases = factory.List([factory.Faker('sentence', nb_words=1) for _ in range(3)])
    description = factory.Faker('text')
