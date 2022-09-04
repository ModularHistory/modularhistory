"""Model class for proposition supports."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.relations.moderated import ModeratedPositionedRelation


class ArgumentSupport(ModeratedPositionedRelation):
    """A support of an argument by a proposition."""

    premise = models.ForeignKey(
        to='propositions.Proposition',
        on_delete=models.CASCADE,
        related_name='_argument_supports',
    )
    argument = models.ForeignKey(
        to='propositions.Argument',
        on_delete=models.CASCADE,
        related_name='_supports',
    )

    class Meta:
        unique_together = [
            ['argument', 'premise'],
            ['position', 'argument'],
        ]
        verbose_name = _('support')

    def __str__(self) -> str:
        """Return the proposition relationship's string representation."""
        return f'Support #{self.position}: {self.premise}'
