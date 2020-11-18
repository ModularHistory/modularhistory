"""Occurrence chains."""

from typing import List

from django.db.models import CASCADE, ForeignKey

from modularhistory.fields import HTMLField
from modularhistory.models import Model

DESCRIPTION_MAX_LENGTH = 200


class OccurrenceChain(Model):
    """A chain of related occurrences."""

    description = HTMLField(null=True, unique=True, paragraphed=True)
    parent_chain = ForeignKey('self', on_delete=CASCADE, related_name='sub_chains')

    def __str__(self):
        """Return the string representation of the occurrence chain."""
        return f'{self.description}'


class OccurrenceChainInclusion(Model):
    """An inclusion of an occurrence in an occurrence chain."""

    chain = ForeignKey(
        OccurrenceChain, on_delete=CASCADE, related_name='occurrence_inclusions'
    )
    occurrence = ForeignKey(
        'occurrences.Occurrence', on_delete=CASCADE, related_name='chain_inclusions'
    )

    class Meta:
        unique_together: List[str] = ['chain', 'occurrence']

    def __str__(self):
        """Return the string representation of the occurrence chain inclusion."""
        return f'{self.chain} : {self.occurrence}'
