"""
Responders to Django signals for the entities app.
"""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.entities import models
from apps.moderation.signals import process_relation_changes


@receiver(m2m_changed, sender=models.ImageRelation)
def respond_to_entity_images_changes(
    sender: models.ImageRelation, instance: models.Entity, **kwargs
):
    """Respond to creation/modification of a Entity-images relationship."""
    process_relation_changes(
        sender, instance, 'image', instance.image_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.TopicRelation)
def respond_to_entity_tags_changes(
    sender: models.TopicRelation, instance: models.Entity, **kwargs
):
    """Respond to creation/modification of a Entity-tags/topics relationship."""
    process_relation_changes(
        sender, instance, 'topic', instance.topic_relations.all(), **kwargs
    )
