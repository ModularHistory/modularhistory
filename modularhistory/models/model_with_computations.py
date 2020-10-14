"""Base classes for models that appear in ModularHistory search results."""

from modularhistory.fields import JSONField
from modularhistory.models.model import Model


class ModelWithComputations(Model):
    """
    A model with computed fields to be stored in JSON (to reduce db queries).

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    computations = JSONField(null=True, blank=True, default=dict)

    class Meta:
        abstract = True
