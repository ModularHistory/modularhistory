"""Base classes for models that appear in ModularHistory search results."""

import re
import uuid
from typing import Match, TYPE_CHECKING

from django.db.models import BooleanField, UUIDField

from modularhistory.models.taggable_model import TaggableModel

if TYPE_CHECKING:
    from modularhistory.models.manager import SearchableModelManager


class SearchableModel(TaggableModel):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    verified = BooleanField(default=False, blank=True)
    hidden = BooleanField(
        default=False,
        blank=True,
        help_text="Don't let this item appear in search results.",
    )
    key = UUIDField(primary_key=False, default=uuid.uuid4, editable=False, unique=True)

    class FieldNames(TaggableModel.FieldNames):
        verified = 'verified'
        hidden = 'hidden'

    class Meta:
        abstract = True

    objects: 'SearchableModelManager'

    # group 1: model class name
    # group 2: model instance pk
    # group 3: ignore
    # group 4: model instance HTML
    # group 5: closing brackets
    admin_placeholder_regex = re.compile(
        r'<<\ ?([a-zA-Z]+?):\ ?([\w\d-]+?)(:\ ?(?!>>)([\s\S]+?))?(\ ?>>)'
    )

    @classmethod
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        placeholder = match.group(0)
        appendage = match.group(3)
        updated_appendage = f': {cls.get_object_html(match)}'
        if appendage:
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            updated_placeholder = (
                f'{placeholder.replace(" >>", "").replace(">>", "")}'
                f'{updated_appendage} >>'
            )
        return updated_placeholder.replace('\n\n\n', '\n').replace('\n\n', '\n')

    @classmethod
    def get_object_from_placeholder(cls, match: Match) -> 'SearchableModel':
        """Given a regex match of a model instance placeholder, return the instance."""
        if not cls.admin_placeholder_regex.match(match.group(0)):
            raise ValueError(f'{match} does not match {cls.admin_placeholder_regex}')
        key = match.group(1).strip()
        return cls.objects.get(pk=key)
