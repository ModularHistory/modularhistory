"""This module provides a `ModelWithPostulations` abstract model."""

# from abc import abstractmethod

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import AbstractModelMeta, Model


class ModelWithPostulations(Model, metaclass=AbstractModelMeta):
    """
    A model with one or more postulations per instance.

    Models with a m2m relationship with postulations (e.g., occurrences,
    quotes, etc.) should inherit from this model.
    """

    postulations = models.ManyToManyField(
        to='postulations.Postulation',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('postulations'),
    )

    # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for ModelWithPostulations."""

        abstract = True
