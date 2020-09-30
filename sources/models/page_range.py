import re
from typing import Optional, Union

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.db.models import CASCADE, ForeignKey, PositiveSmallIntegerField
from django.utils.html import SafeString, format_html

from modularhistory.models import Model


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
        return BeautifulSoup(self.html, features='lxml').get_text()

    @property
    def html(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        citation = self.citation
        if not self.page_number:
            return None
        pn = self.page_number
        end_pn = self.end_page_number or None
        _url = citation.source.file_url or None

        def get_page_number_url(page_number, url=_url) -> Optional[str]:
            if not url:
                return None
            page_number += citation.source.file.page_offset
            if 'page=' in url:
                url = re.sub(r'page=\d+', f'page={page_number}', url)
            else:
                url = f'{url}#page={page_number}'
            return url

        def get_page_number_link(url: str, page_number: Union[str, int]) -> Optional[str]:
            if not url:
                return None
            return (
                f'<a href="{url}" target="_blank" '
                f'class="display-source">{page_number}</a>'
            )

        pn_url = get_page_number_url(pn)
        pn_html = get_page_number_link(pn_url, pn) or str(pn)
        if end_pn:
            end_pn_url = get_page_number_url(end_pn)
            end_pn_html = get_page_number_link(end_pn_url, end_pn) or str(end_pn)
            page_html = f'pp. {pn_html}–{end_pn_html}'
        else:
            page_html = f'p. {pn_html}'
        return format_html(page_html)

    def clean(self):
        """TODO: add docstring."""
        if self.end_page_number and self.end_page_number < self.page_number:
            raise ValidationError('The end page number must be greater than the start page number.')
