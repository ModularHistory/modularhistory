"""Classes for models with relations to sources."""

from typing import Any, Optional, TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.models import retrieve_or_compute
from modularhistory.models.searchable_model import SearchableModel

if TYPE_CHECKING:
    from sources.models import Citation


class ModelWithSources(SearchableModel):
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
        """Return the quote's primary citation, if a citation exists."""
        try:
            return self.citations.order_by('position')[0]
        except IndexError:
            return None

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='citation_html', caster=format_html)
    def citation_html(self) -> Optional[SafeString]:
        """Return the quote's citation HTML, if a citation exists."""
        if self.citations.exists():  # TODO: use try-except instead of making this query
            citation_html = '; '.join(
                [citation.html for citation in self.citations.all()]
            )
            return format_html(citation_html)
        return None
