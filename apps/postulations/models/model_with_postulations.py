"""This module provides a `ModelWithPostulations` abstract model."""

from abc import abstractmethod


from core.models import AbstractModelMeta, Model


class ModelWithPostulations(Model, metaclass=AbstractModelMeta):
    """
    A model with one or more postulations per instance.

    Models that can be expected to have a m2m relationship with postulations
    (e.g., occurrences, quotes, etc.) should inherit from this model.
    """

    # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for ModelWithPostulations."""

        abstract = True

    @property
    @abstractmethod
    def postulations(self):
        pass
