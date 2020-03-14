from typing import Any, Optional, TYPE_CHECKING

from django.db.models import (
    Model as BaseModel
)
from django.utils.safestring import SafeText, mark_safe

if TYPE_CHECKING:
    from sources.models import SourceReference


class SourceMixin(BaseModel):
    sources: Any  # Defined in model
    source_references: Any  # Defined in model

    class Meta:
        abstract = True

    @property
    def source_file_url(self) -> Optional[str]:
        if self.source_reference:
            return self.source_reference.source_file_url
        return None

    @property
    def source_reference(self) -> Optional['SourceReference']:
        if not len(self.sources.all()):
            return None
        return self.source_references.order_by('position')[0]

    @property
    def source_reference_html(self) -> Optional[SafeText]:
        if self.source_reference:
            return mark_safe(self.source_reference.html)
        return None
