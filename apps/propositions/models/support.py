"""Model class for proposition supports."""

from django.db import models

from core.models import PositionedRelation


class Support(PositionedRelation):
    """A support of a proposition by another proposition."""

    premise = models.ForeignKey(
        to='propositions.Proposition',
        on_delete=models.CASCADE,
        related_name='supports',
    )
    new_premise = models.ForeignKey(
        to='propositions.TypedProposition',
        on_delete=models.CASCADE,
        related_name='supports',
        null=True,
    )

    conclusion = models.ForeignKey(
        to='propositions.Proposition',
        on_delete=models.CASCADE,
        related_name='conclusion_supports',
    )
    new_conclusion = models.ForeignKey(
        to='propositions.TypedProposition',
        on_delete=models.CASCADE,
        related_name='conclusion_supports',
        null=True,
    )
