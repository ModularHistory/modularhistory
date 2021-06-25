from typing import Type

from django.db.models.base import Model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.propositions.models.proposition import get_proposition_fk


class Conflict(Model):
    """
    A conflict between two propositions.

    Conflicts must be symmetrical; i.e., for a conflict between propositions A and B,
    two `Conflict` instances must be created: one with `proposition` set to A and
    `conflicting_proposition` set to B, and one with `proposition` set to B and
    `conflicting_proposition` set to A. To manage this, we use `post_save` and
    `post_delete` signals.
    """

    proposition = get_proposition_fk(related_name='inward_conflicts')
    conflicting_proposition = get_proposition_fk(related_name='outward_conflicts')


@receiver(post_save, sender=Conflict)
def post_save(sender: Type[Conflict], instance: Conflict, created: bool, **kwargs):
    """Respond to the post_save signal."""
    # If saving a new conflict, add a complimentary conflict with `proposition` and
    # `conflicting_proposition` reversed.
    if created:
        sender.objects.get_or_create(
            proposition=instance.conflicting_proposition,
            conflicting_proposition=instance.proposition,
        )


@receiver(post_delete, sender=Conflict)
def post_delete(sender: Type[Conflict], instance: Conflict, **kwargs):
    """Respond to the post_delete signal."""
    # Delete the conflict's complimentary conflict.
    sender.objects.filter(
        proposition=instance.conflicting_proposition,
        conflicting_proposition=instance.proposition,
    ).delete()
