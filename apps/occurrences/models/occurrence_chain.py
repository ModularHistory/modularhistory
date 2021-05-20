"""Occurrence chains."""

from typing import List

from django.db import models

from core.fields import HTMLField
from core.models.model import Model

DESCRIPTION_MAX_LENGTH = 200


class OccurrenceChain(Model):
    """A chain of related occurrences."""

    description = HTMLField(null=True, unique=True, paragraphed=True)
    parent_chain = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='sub_chains'
    )

    def __str__(self):
        """Return the string representation of the occurrence chain."""
        return f'{self.description}'


class OccurrenceChainInclusion(Model):
    """An inclusion of an occurrence in an occurrence chain."""

    chain = models.ForeignKey(
        to='occurrences.OccurrenceChain',
        on_delete=models.CASCADE,
        related_name='occurrence_inclusions',
    )
    occurrence = models.ForeignKey(
        to='propositions.Occurrence',
        on_delete=models.CASCADE,
        related_name='chain_inclusions',
    )

    class Meta:
        """Meta options for OccurrenceChainInclusion."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together: List[str] = ['chain', 'occurrence']

    def __str__(self):
        """Return the string representation of the occurrence chain inclusion."""
        return f'{self.chain} : {self.occurrence}'
