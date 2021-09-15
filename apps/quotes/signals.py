"""
Responders to Django signals for the quote app.
"""

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.quotes import models


@receiver(m2m_changed, sender=models.ImageRelation)
def respond_to_quote_images_changes(
    sender: models.ImageRelation, instance: models.Quote, **kwargs
):
    """Respond to creation/modification of a quote-images relationship."""
    action = kwargs.pop('action', None)
    pk_set = kwargs.pop('pk_set', set())

    if action == 'post_add':
        for image_relation in instance.image_relations.all().filter(image__in=pk_set):
            # re-save relation to trigger moderation
            image_relation.save()
