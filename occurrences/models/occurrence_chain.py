# type: ignore
# TODO: remove above line after fixing typechecking
from typing import List

from django.db.models import ForeignKey, CASCADE

from history.fields import HTMLField
from history.models import Model


class OccurrenceChain(Model):
    """TODO: add docstring."""

    description = HTMLField(max_length=200, null=True, unique=True)
    parent_chain = ForeignKey('self', on_delete=CASCADE, related_name='sub_chains')


class OccurrenceChainInclusion(Model):
    """TODO: add docstring."""

    chain = ForeignKey(
        OccurrenceChain,
        on_delete=CASCADE,
        related_name='occurrence_inclusions'
    )
    occurrence = ForeignKey(
        'occurrences.Occurrence',
        on_delete=CASCADE,
        related_name='chain_inclusions'
    )

    class Meta:
        unique_together: List[str] = ['chain', 'occurrence']
