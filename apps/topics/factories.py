from factory.django import DjangoModelFactory

from apps.topics import models


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = models.Topic
