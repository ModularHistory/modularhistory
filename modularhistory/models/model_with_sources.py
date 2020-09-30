"""Classes for models with relations to sources."""

from typing import Any, Optional, TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.utils.html import SafeString, format_html

from modularhistory.models.model import Model

if TYPE_CHECKING:
    from sources.models import Citation


class ModelWithSources(Model):
    """
    A model that has sources; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    sources: Any

    citations = GenericRelation('sources.Citation')

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
        """TODO: write docstring."""
        if not len(self.citations.all()):
            return None
        return self.citations.order_by('position')[0]

    @property
    def citation_html(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        if not self.citations.exists():
            return None
        citations = self.citations.all()
        primary_citation = citations[0]
        citation_html = primary_citation.html
        if len(citations) > 1:
            prev_citation = primary_citation
            for citation in citations[1:]:
                more_html = citation.html
                if citation.source.attributee_string == prev_citation.source.attributee_string:
                    more_html = more_html[len(f'{citation.source.attributee_string}, '):]
                citation_html = f'{citation_html}; {more_html}'
        citations = '; '.join([citation.html for citation in self.citations.all()])
        return format_html(citations)
