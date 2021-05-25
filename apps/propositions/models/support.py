"""Model class for proposition supports."""

from django.db import models

from core.models import PositionedRelation


class Support(PositionedRelation):
    """A support of a proposition by another proposition."""

    premise = models.ForeignKey(
        to='propositions.TypedProposition',
        on_delete=models.CASCADE,
        related_name='supports',
    )
    conclusion = models.ForeignKey(
        to='propositions.TypedProposition',
        on_delete=models.CASCADE,
        related_name='conclusion_supports',
    )

    def __str__(self) -> str:
        return f'{self.premise} --> {self.conclusion}'
