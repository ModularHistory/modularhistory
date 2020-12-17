"""Base classes for models that appear in ModularHistory search results."""

from apps.dates.models import DatedModel

from .searchable_model import SearchableModel


class SearchableDatedModel(SearchableModel, DatedModel):
    """
    A dated model that shows up in search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    class Meta:
        """
        Meta options for SearchableDatedModel.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True

    class FieldNames(SearchableModel.FieldNames, DatedModel.FieldNames):
        """Field names used by SearchableDatedModel."""

        pass
