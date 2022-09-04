import factory

from apps.moderation.factories import ModeratedModelFactory
from apps.topics import models


class TopicFactory(ModeratedModelFactory):
    class Meta:
        model = models.Topic

    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    name = factory.Sequence(lambda n: f'Topic{n}')
    aliases = factory.List([factory.Faker('sentence', nb_words=1) for _ in range(3)])
    description = factory.Faker('text')
