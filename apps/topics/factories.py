import factory

from apps.moderation.factories import ModeratedModelFactory
from apps.topics import models
from core.factories import UniqueFaker


class TopicFactory(ModeratedModelFactory):
    class Meta:
        model = models.Topic

    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    name = UniqueFaker('sentence', nb_words=1)
    aliases = factory.List([factory.Faker('sentence', nb_words=1) for _ in range(3)])
    description = factory.Faker('text')
