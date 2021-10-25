"""
Responders to Django signals for the quote app.
"""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.moderation.signals import process_relation_changes
from apps.propositions import models


@receiver(m2m_changed, sender=models.ImageRelation)
def respond_to_proposition_images_changes(
    sender: models.ImageRelation, instance: models.Proposition, **kwargs
):
    """Respond to creation/modification of a proposition-images relationship."""
    process_relation_changes(
        sender, instance, 'image', instance.image_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.TopicRelation)
def respond_to_proposition_tags_changes(
    sender: models.TopicRelation, instance: models.Proposition, **kwargs
):
    """Respond to creation/modification of a proposition-tags/topics relationship."""
    process_relation_changes(
        sender, instance, 'topic', instance.topic_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.Citation)
def respond_to_proposition_citations_changes(
    sender: models.Citation, instance: models.Proposition, **kwargs
):
    """Respond to creation/modification of a proposition-citations relationship."""
    process_relation_changes(sender, instance, 'source', instance.citations.all(), **kwargs)


@receiver(m2m_changed, sender=models.Argument)
def respond_to_proposition_argument_changes(
    sender: models.Argument, instance: models.Proposition, **kwargs
):
    """Respond to creation/modification of a proposition-arguments relationship."""
    process_relation_changes(sender, instance, 'source', instance.arguments.all(), **kwargs)
