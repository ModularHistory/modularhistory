from typing import Any, Optional, TYPE_CHECKING

from django.db.models import (
    Model as BaseModel
)
from django.utils.safestring import SafeText, mark_safe

if TYPE_CHECKING:
    from sources.models import SourceReference


class SourceMixin(BaseModel):
    sources: Any  # Defined in model
    citations: Any  # Defined in model

    class Meta:
        abstract = True

    @property
    def source_file_url(self) -> Optional[str]:
        if self.citation:
            return self.citation.source_file_url
        return None

    @property
    def citation(self) -> Optional['SourceReference']:
        if not len(self.sources.all()):
            return None
        return self.citations.order_by('position')[0]

    @property
    def citation_html(self) -> Optional[SafeText]:
        if self.citation:
            return mark_safe(self.citation.html)
        return None
