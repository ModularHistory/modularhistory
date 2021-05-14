"""This module provides a `ModelWithPropositions` abstract model."""

# from abc import abstractmethod

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import AbstractModelMeta, Model


class ModelWithPropositions(Model, metaclass=AbstractModelMeta):
    """
    A model with one or more propositions per instance.

    Models with a m2m relationship with propositions should inherit from this model.
    """

    propositions = models.ManyToManyField(
        to='propositions.Proposition',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('propositions'),
    )

    # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for ModelWithPropositions."""

        abstract = True
