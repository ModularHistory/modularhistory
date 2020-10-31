"""Classes for models with relations to sources."""

from typing import TYPE_CHECKING, Dict, List, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.constants import EMPTY_STRING
from modularhistory.models import Model, retrieve_or_compute
from sources.serializers import CitationSerializer

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

    from sources.models import Citation


class ModelWithSources(Model):
    """
    A model that has sources; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    citations = GenericRelation('sources.Citation')
    sources: 'RelatedManager'

    class Meta:
        abstract = True

    @property
    def source_file_url(self) -> Optional[str]:
        """TODO: write docstring."""
        if self.citation:
            return self.citation.source_file_url
        return None

    @property
    def citation(self) -> Optional['Citation']:
        """Return the quote's primary citation, if a citation exists."""
        try:
            return self.citations.order_by('position')[0]
        except IndexError:
            return None

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='serialized_citations')
    def serialized_citations(self) -> List[Dict]:
        """Return a list of dictionaries representing the instance's citations."""
        return [CitationSerializer(citation).data for citation in self.citations.all()]

    @property
    def citation_html(self) -> SafeString:
        """Return the instance's full citation HTML."""
        try:
            citation_html = '; '.join(
                citation['html'] for citation in self.serialized_citations
            )
        except (ObjectDoesNotExist, AttributeError, ValueError):
            citation_html = EMPTY_STRING
        return format_html(citation_html)
