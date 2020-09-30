"""Base classes for models that appear in ModularHistory search results."""

import uuid

from django.db.models import BooleanField, UUIDField

from modularhistory.models.taggable_model import TaggableModel


class SearchableModel(TaggableModel):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    verified = BooleanField(default=False, blank=True)
    hidden = BooleanField(
        default=False, blank=True,
        help_text="Don't let this item appear in search results."
    )
    key = UUIDField(primary_key=False, default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True
