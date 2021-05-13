"""Model class for postulation supports."""

from django.db import models

from apps.postulations.models.fact_relation import FactRelation


class PostulationSupport(FactRelation):
    """A supportion of a fact by another fact."""

    supported_postulation = models.ForeignKey(
        to='postulations.Postulation',
        on_delete=models.CASCADE,
        related_name='supported_postulation_supports',
    )
    supportive_postulation = models.ForeignKey(
        to='postulations.Postulation',
        on_delete=models.CASCADE,
        related_name='supportive_postulation_supports',
    )
