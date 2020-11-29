"""Base classes for models that appear in ModularHistory search results."""

import uuid
from typing import TYPE_CHECKING

import serpy
from django.db.models import BooleanField, UUIDField

from modularhistory.models.model import ModelSerializer
from modularhistory.models.model_with_computations import ModelWithComputations
from topics.models.taggable_model import TaggableModel
from verifications.models import VerifiableModel

if TYPE_CHECKING:
    from search.models.manager import SearchableModelManager


class SearchableModel(TaggableModel, ModelWithComputations, VerifiableModel):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    key = UUIDField(primary_key=False, default=uuid.uuid4, editable=False, unique=True)
    hidden = BooleanField(
        default=False,
        blank=True,
        help_text="Don't let this item appear in search results.",
    )

    class FieldNames(TaggableModel.FieldNames):
        verified = 'verified'
        hidden = 'hidden'

    class Meta:
        abstract = True

    objects: 'SearchableModelManager'


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    key = serpy.StrField()
    tags_html = serpy.Field()
