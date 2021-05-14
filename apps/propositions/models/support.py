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
    conclusion = models.ForeignKey(
        to='propositions.Proposition',
        on_delete=models.CASCADE,
        related_name='conclusion_supports',
    )
