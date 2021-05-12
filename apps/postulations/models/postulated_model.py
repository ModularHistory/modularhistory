"""This module provides a `ModelWithPostulations` abstract model."""

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.model_with_sources import ModelWithSources
from core.models import AbstractModelMeta, Model

if TYPE_CHECKING:
    pass


class PostulatedModel(ModelWithSources, metaclass=AbstractModelMeta):
    """
    Abstract base model for postulated models.

    Models of which instances are postulated, i.e., presented as information that
    can be analyzed and determined to be true or false with some degree of certainty,
    should inherit from this model.
    """

    postulation = models.OneToOneField(
        to='postulations.Postulation',
        on_delete=models.PROTECT,
        verbose_name=_('postulation'),
    )

    # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for ModelWithPostulations."""

        abstract = True
