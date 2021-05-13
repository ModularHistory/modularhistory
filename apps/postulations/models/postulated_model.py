"""This module provides a `ModelWithPostulations` abstract model."""

from polymorphic.models import PolymorphicModel

from apps.sources.models.model_with_sources import ModelWithSources


class PolymorphicProposition(PolymorphicModel, ModelWithSources):
    """
    Abstract base model for postulated models.

    Models of which instances are postulated, i.e., presented as information that
    can be analyzed and determined to be true or false with some degree of certainty,
    should inherit from this model.
    """
