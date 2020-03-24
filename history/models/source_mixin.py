from typing import Any, Optional, TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db.models import (
    Model as BaseModel
)
# from gm2m import GM2MField as GenericManyToManyField
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
        if not self.sources.exists():
            return None
        citations = '; '.join([citation.html for citation in self.citations.all()])
        return mark_safe(citations)

    def clean(self):
        super().clean()
        # TODO: Do this check in forms rather than in the model, since there's already some bad data
        # if len(self.citations.filter(position=1)) > 1:
        #     raise ValidationError('Citation positions should be unique.')
