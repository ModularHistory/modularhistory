"""
Responders to Django signals for the quote app.
"""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.moderation.signals import process_relation_changes
from apps.quotes import models


@receiver(m2m_changed, sender=models.ImageRelation)
def respond_to_quote_images_changes(
    sender: models.ImageRelation, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-images relationship."""
    process_relation_changes(
        sender, instance, 'image', instance.image_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.QuoteAttribution)
def respond_to_quote_attributions_changes(
    sender: models.QuoteAttribution, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-attributees relationship."""
    process_relation_changes(
        sender, instance, 'attributee', instance.attributions.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.TopicRelation)
def respond_to_quote_tags_changes(
    sender: models.TopicRelation, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-tags/topics relationship."""
    process_relation_changes(
        sender, instance, 'topic', instance.topic_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.QuoteRelation)
def respond_to_quote_related_quotes_changes(
    sender: models.QuoteRelation, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-related_quotes relationship."""
    process_relation_changes(
        sender, instance, 'quote', instance.quote_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.EntityRelation)
def respond_to_quote_entities_changes(
    sender: models.EntityRelation, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-entities relationship."""
    process_relation_changes(
        sender, instance, 'entity', instance.entity_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.Citation)
def respond_to_quote_citations_changes(
    sender: models.Citation, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-citations relationship."""
    process_relation_changes(sender, instance, 'source', instance.citations.all(), **kwargs)
