from typing import TYPE_CHECKING

import serpy

from apps.search.api.serializers import SearchableModelSerializer
from core.models.model import ModelSerializer

if TYPE_CHECKING:
    from apps.propositions.models import Occurrence


class PropositionSerializer(ModelSerializer):
    """Serializer for propositions."""

    slug = serpy.StrField()
    summary = serpy.StrField()
    elaboration = serpy.StrField()
    dateString = serpy.StrField(attr='date_string')
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')
    tagsHtml = serpy.StrField(attr='tags_html')

    def get_model(self, instance) -> str:
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'


class OccurrenceSerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    summary = serpy.StrField()
    elaboration = serpy.StrField()
    postscript = serpy.StrField()
    dateString = serpy.StrField(attr='date_string')
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')
    tagsHtml = serpy.StrField(attr='tags_html')

    def get_model(self, instance: 'Occurrence') -> str:
        """Return the model name of the instance."""
        return 'propositions.occurrence'
