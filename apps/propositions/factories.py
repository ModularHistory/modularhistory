import factory
from factory import fuzzy

from apps.images.factories import ImageFactory
from apps.moderation.factories import ModeratedModelFactory
from apps.propositions import models
from apps.topics.factories import TopicFactory


class PropositionFactory(ModeratedModelFactory):
    class Meta:
        model = models.Proposition

    title = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    type = fuzzy.FuzzyChoice(x[0] for x in models.TYPE_CHOICES)
    elaboration = factory.Faker('text')
    summary = factory.Faker('text')
    date = factory.Faker('historic_datetime')
    end_date = factory.Faker('historic_datetime')


class TopicRelationFactory(ModeratedModelFactory):
    class Meta:
        model = models.TopicRelation

    content_object = factory.SubFactory(PropositionFactory)
    topic = factory.SubFactory(TopicFactory)


class ImageRelationFactory(ModeratedModelFactory):
    class Meta:
        model = models.ImageRelation

    content_object = factory.SubFactory(PropositionFactory)
    image = factory.SubFactory(ImageFactory)


class PropositionWithRelatedObjectsFactory(ModeratedModelFactory):
    class Meta:
        model = models.Proposition

    image_relations = factory.RelatedFactoryList(
        ImageRelationFactory,
        factory_related_name='content_object',
    )

    topic_relations = factory.RelatedFactoryList(
        TopicRelationFactory,
        factory_related_name='content_object',
    )
