"""Model class for fact supportations."""

from django.db import models

from apps.postulations.models.fact_relation import FactRelation


class PostulationSupport(FactRelation):
    """A supportion of a fact by another fact."""

    supported_fact = models.ForeignKey(
        to='postulations.Postulation',
        on_delete=models.CASCADE,
        related_name='supported_fact_supports',
    )
    supportive_fact = models.ForeignKey(
        to='postulations.Postulation',
        on_delete=models.CASCADE,
        related_name='supportive_fact_supports',
    )
