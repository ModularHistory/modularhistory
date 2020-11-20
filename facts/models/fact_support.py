"""Model class for fact supportations."""

from django.db.models import CASCADE, ForeignKey
from facts.models.fact_relation import FactRelation


class FactSupport(FactRelation):
    """A supportion of a fact by another fact."""

    supported_fact = ForeignKey(
        'facts.Fact', on_delete=CASCADE, related_name='supported_fact_supports'
    )
    supportive_fact = ForeignKey(
        'facts.Fact', on_delete=CASCADE, related_name='supportive_fact_supports'
    )
