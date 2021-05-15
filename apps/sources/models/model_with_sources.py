"""Classes for models with relations to sources."""

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from concurrency.fields import IntegerVersionField
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.html import format_html
from django.utils.safestring import SafeString

from core.constants.strings import EMPTY_STRING
from core.fields import HTMLField
from core.models.model import Model
from core.models.model_with_computations import retrieve_or_compute

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

    from apps.sources.models.citation import Citation
    from apps.sources.models.source import Source


class ModelWithSources(Model):
    """
    A model that has sources; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    citations = GenericRelation('sources.Citation')
    sources: 'RelatedManager[Source]'

    version = IntegerVersionField()

    # Admin-facing notes (not to be displayed to users)
    notes = HTMLField(null=True, blank=True, paragraphed=True, processed=False)

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
        return [citation.serialize() for citation in self.citations.all()]

    @property
    def citation_html(self) -> SafeString:
        """Return the instance's full citation HTML."""
        try:
            citation_html = '; '.join(
                citation.get('html') for citation in self.serialized_citations
            )
        except Exception as error:
            logging.error(f'{error}')
            citation_html = EMPTY_STRING
        return format_html(citation_html)
