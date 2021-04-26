"""Base classes for models that appear in ModularHistory search results."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.dates.models import DatedModel

from .searchable_model import SearchableModel


class SearchableDatedModel(SearchableModel, DatedModel):
    """
    A dated model that shows up in search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    title = models.CharField(
        verbose_name=_('title'),
        max_length=120,
        null=True,
        blank=True,
        help_text=(
            "The title can be used for the detail page header and title tag, "
            "SERP result card header, etc."
        ),
    )

    class Meta:
        """Meta options for SearchableDatedModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        abstract = True

    class FieldNames(SearchableModel.FieldNames, DatedModel.FieldNames):
        """Field names used by SearchableDatedModel."""
