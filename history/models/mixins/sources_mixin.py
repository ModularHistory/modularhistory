from typing import Any, Optional, TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from history.models.model import BaseModel
from django.utils.safestring import SafeText, mark_safe

if TYPE_CHECKING:
    from sources.models import Citation


class SourcesMixin(BaseModel):
    sources: Any

    citations = GenericRelation('sources.Citation')

    class Meta:
        abstract = True

    @property
    def source_file_url(self) -> Optional[str]:
        if self.citation:
            return self.citation.source_file_url
        return None

    @property
    def citation(self) -> Optional['Citation']:
        if not len(self.citations.all()):
            return None
        return self.citations.order_by('position')[0]

    @property
    def citation_html(self) -> Optional[SafeText]:
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
                citation_html += f'; {more_html}'
        citations = '; '.join([citation.html for citation in self.citations.all()])
        return mark_safe(citations)

    def clean(self):
        super().clean()
        # TODO: Do this check in forms rather than in the model, since there's already some bad data
        # if len(self.citations.filter(position=1)) > 1:
        #     raise ValidationError('Citation positions should be unique.')
