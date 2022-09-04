from apps.propositions import models
from apps.propositions.factories import PropositionFactory


class OccurrenceFactory(PropositionFactory):
    class Meta:
        model = models.Occurrence

    type = 'propositions.occurrence'
