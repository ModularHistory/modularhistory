from django.db.models import ForeignKey, CASCADE

from history.fields import HTMLField
from history.models import Model


class OccurrenceChain(Model):
    description = HTMLField(max_length=200, null=True, unique=True)
    parent_chain = ForeignKey('self', on_delete=CASCADE, related_name='sub_chains')


class OccurrenceChainInclusion(Model):
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
        unique_together = ['chain', 'occurrence']