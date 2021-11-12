"""
Responders to Django signals for the sources app.

The choice of using post_save and pre_delete receivers on intermediate models for
m2m relationships, as opposed to simply using receivers for the m2m_changed signal,
is due to limitations of inline model admins. See:
https://github.com/django/django/commit/9d104a21e20f9c5ec41d19fd919d0e808aa13dba
"""

from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from apps.moderation.signals import process_relation_changes
from apps.sources import models
from apps.sources.tasks import update_source


def process_post_save(source: models.Source):
    """Respond to the saving of a source m2m relationship."""
    source.update_calculated_fields()
    source.save(moderate=False)  # TODO: is this OK?


def process_pre_delete(source: models.Source):
    """Respond to the deletion of a source m2m relationship."""
    # TODO: Make this safer and better.
    # Queue up a task to update the source after waiting 20 seconds (for the
    # deletion of the containment to be complete, presumably).
    update_source.apply_async(args=[source.pk], countdown=20)


@receiver(post_save, sender=models.SourceAttribution)
def respond_to_source_attribution_save(sender, instance: models.SourceAttribution, **kwargs):
    """Respond to creation/modification of a source-attributee relationship."""
    process_post_save(instance.source)


@receiver(pre_delete, sender=models.SourceAttribution)
def respond_to_source_attribution_deletion(
    sender, instance: models.SourceAttribution, **kwargs
):
    """Respond to deletion of a source-attributee relationship."""
    process_pre_delete(instance.source)


@receiver(post_save, sender=models.SourceContainment)
def respond_to_source_containment_save(sender, instance: models.SourceContainment, **kwargs):
    """Respond to creation/modification of a source-container relationship."""
    process_post_save(instance.source)


@receiver(pre_delete, sender=models.SourceContainment)
def respond_to_source_containment_deletion(
    sender, instance: models.SourceContainment, **kwargs
):
    """Respond to deletion of a source-container relationship."""
    process_pre_delete(instance.source)


@receiver(m2m_changed, sender=models.SourceContainment)
def respond_to_source_containment_changes(
    sender: models.SourceContainment, instance: models.Source, **kwargs
):
    """Respond to creation/modification of a source-source_containment relationship."""
    process_relation_changes(
        sender, instance, 'source', instance.source_containments.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.TopicRelation)
def respond_to_source_tags_changes(
    sender: models.TopicRelation, instance: models.Source, **kwargs
):
    """Respond to creation/modification of a source-tags/topics relationship."""
    process_relation_changes(
        sender, instance, 'topic', instance.topic_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.EntityRelation)
def respond_to_source_related_entities_changes(
    sender: models.EntityRelation, instance: models.Source, **kwargs
):
    """Respond to creation/modification of a source-related_entities relationship."""
    process_relation_changes(
        sender, instance, 'entity', instance.entity_relations.all(), **kwargs
    )


@receiver(m2m_changed, sender=models.SourceAttribution)
def respond_to_source_attributions_changes(
    sender: models.SourceAttribution, instance: models.Source, **kwargs
):
    """Respond to creation/modification of a source-attributees relationship."""
    process_relation_changes(
        sender, instance, 'attributee', instance.attributions.all(), **kwargs
    )
