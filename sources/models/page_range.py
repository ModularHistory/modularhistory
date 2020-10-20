from typing import Optional

from django.core.exceptions import ValidationError
from django.db.models import CASCADE, ForeignKey, PositiveSmallIntegerField
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.models import Model
from modularhistory.utils.html import soupify


class PageRange(Model):
    """TODO: add docstring."""

    citation = ForeignKey('sources.Citation', on_delete=CASCADE, related_name='pages')
    page_number = PositiveSmallIntegerField()
    end_page_number = PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ['citation', 'page_number']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return soupify(self.html).get_text()

    @property
    def html(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        citation = self.citation
        if not self.page_number:
            return None
        pn, end_pn = self.page_number, self.end_page_number or None
        pn_url = citation.get_page_number_url(pn)
        pn_html = citation.get_page_number_link(pn, pn_url) or str(pn)
        if end_pn:
            end_pn_url = citation.get_page_number_url(end_pn)
            end_pn_html = citation.get_page_number_link(end_pn, end_pn_url) or str(end_pn)
            pn_html = f'pp. {pn_html}–{end_pn_html}'
        else:
            pn_html = f'p. {pn_html}'
        return format_html(pn_html)

    def clean(self):
        """TODO: add docstring."""
        if self.end_page_number and self.end_page_number < self.page_number:
            raise ValidationError('The end page number must be greater than the start page number.')
