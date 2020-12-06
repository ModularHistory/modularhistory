from typing import Optional

from django.core.exceptions import ValidationError
from django.db.models import CASCADE, ForeignKey, PositiveSmallIntegerField
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.models import Model
from modularhistory.utils.html import soupify


class PageRange(Model):
    """TODO: add docstring."""

    citation = ForeignKey(
        to='sources.Citation', on_delete=CASCADE, related_name='pages'
    )
    page_number = PositiveSmallIntegerField()
    end_page_number = PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ['citation', 'page_number']

    def __str__(self) -> str:
        """Return the page range's string representation."""
        return soupify(self.html).get_text()

    def clean(self):
        """Prepare the page range to be saved."""
        if self.end_page_number and self.end_page_number < self.page_number:
            raise ValidationError(
                'The end page number must be greater than the start page number.'
            )

    @property
    def html(self) -> Optional[SafeString]:
        """Return the page range's HTML representation."""
        html = self.unprefixed_html
        if html:
            end_pn = self.end_page_number or None
            if end_pn:
                html = f'pp. {html}'
            else:
                html = f'p. {html}'
            return format_html(html)
        return None

    @property
    def unprefixed_html(self) -> Optional[str]:
        """Return the page range's HTML, without any "p." prefix."""
        citation = self.citation
        if not self.page_number:
            return None
        pn, end_pn = self.page_number, self.end_page_number or None
        pn_url = citation.get_page_number_url(pn)
        pn_html = citation.get_page_number_link(pn, pn_url) or str(pn)
        if end_pn:
            end_pn_url = citation.get_page_number_url(end_pn)
            end_pn_html = citation.get_page_number_link(end_pn, end_pn_url) or str(
                end_pn
            )
            pn_html = f'{pn_html}–{end_pn_html}'
        else:
            pn_html = f'{pn_html}'
        return pn_html
