"""
Responders to Django signals for the sources app.

The choice of using post_save and pre_delete receivers on intermediate models for
m2m relationships, as opposed to simply using receivers for the m2m_changed signal,
is due to limitations of inline model admins. See:
https://github.com/django/django/commit/9d104a21e20f9c5ec41d19fd919d0e808aa13dba
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.sources import models
from apps.sources.tasks import update_source


def process_post_save(source: models.Source):
    """Respond to the saving of a source m2m relationship."""
    source.update_calculated_fields()
    source.save()


def process_pre_delete(source: models.Source):
    """Respond to the deletion of a source m2m relationship."""
    # TODO: Make this safer and better.
    # Queue up a task to update the source after waiting 20 seconds (for the
    # deletion of the containment to be complete, presumably).
    update_source.apply_async(args=[source.pk], countdown=20)


@receiver(post_save, sender=models.SourceAttribution)
def respond_to_source_attribution_save(
    sender, instance: models.SourceAttribution, **kwargs
):
    """Respond to creation/modification of a source-attributee relationship."""
    process_post_save(instance.source)


@receiver(pre_delete, sender=models.SourceAttribution)
def respond_to_source_attribution_deletion(
    sender, instance: models.SourceAttribution, **kwargs
):
    """Respond to deletion of a source-attributee relationship."""
    process_pre_delete(instance.source)


@receiver(post_save, sender=models.SourceContainment)
def respond_to_source_containment_save(
    sender, instance: models.SourceContainment, **kwargs
):
    """Respond to creation/modification of a source-container relationship."""
    process_post_save(instance.source)


@receiver(pre_delete, sender=models.SourceContainment)
def respond_to_source_containment_deletion(
    sender, instance: models.SourceContainment, **kwargs
):
    """Respond to deletion of a source-container relationship."""
    process_pre_delete(instance.source)
