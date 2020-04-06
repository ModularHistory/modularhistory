import re
from typing import Optional

from bs4 import BeautifulSoup
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, CASCADE, PositiveSmallIntegerField
from django.utils.safestring import SafeText, mark_safe

from history.models import Model
from sources.models import Source

source_types = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
    ('T', 'Tertiary')
)

citation_phrase_options = (
    (None, ''),
    ('quoted in', 'quoted in'),
    ('cited in', 'cited in')
)


class OSR(Model):
    occurrence = ForeignKey('occurrences.Occurrence', on_delete=CASCADE, related_name='osrs')
    citation_phrase = models.CharField(max_length=10, choices=citation_phrase_options,
                                       default=None, null=True, blank=True)
    source = ForeignKey(Source, related_name='osrs', on_delete=CASCADE)
    page_number = PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = PositiveSmallIntegerField(null=True, blank=True)
    position = PositiveSmallIntegerField(
        default=1, blank=True,
        help_text='Determines the order of references.'
    )


class QSR(Model):
    quote = ForeignKey('quotes.Quote', on_delete=CASCADE, related_name='qsrs')
    citation_phrase = models.CharField(max_length=10, choices=citation_phrase_options,
                                       default=None, null=True, blank=True)
    source = ForeignKey(Source, related_name='qsrs', on_delete=CASCADE)
    page_number = PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = PositiveSmallIntegerField(null=True, blank=True)
    position = PositiveSmallIntegerField(
        default=1, blank=True,
        help_text='Determines the order of references.'
    )


class Citation(Model):
    """A reference to a source (from any other model)."""
    citation_phrase = models.CharField(max_length=10, choices=citation_phrase_options,
                                       default=None, null=True, blank=True)
    source = ForeignKey(Source, related_name='citations', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    page_number = PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = PositiveSmallIntegerField(null=True, blank=True)
    position = PositiveSmallIntegerField(
        default=1, blank=True,
        help_text='Determines the order of references.'
    )

    class Meta:
        unique_together = ['source', 'content_type', 'object_id',
                           'page_number', 'end_page_number', 'position']
        ordering = ['position', 'source', 'page_number']

    def __str__(self):
        return BeautifulSoup(self.html, features='lxml').get_text()

    @property
    def html(self) -> SafeText:
        html = f'{self.source.html}'
        page_string = ''
        if self.page_number:
            pn = self.page_number
            end_pn = self.end_page_number or None
            _url = self.source.file_url or None

            def get_page_number_url(page_number, url=_url) -> Optional[str]:
                if not url:
                    return None
                page_number += self.source.file.page_offset
                if 'page=' in url:
                    url = re.sub(r'page=\d+', f'page={page_number}', url)
                else:
                    url += f'#page={page_number}'
                return url

            def get_page_number_link(url, page_number) -> Optional[str]:
                if not url:
                    return None
                return (f'<a href="{url}" target="_blank" '
                        f'class="display-source">{page_number}</a>')

            pn_url = get_page_number_url(pn)
            pn = get_page_number_link(pn_url, pn) or pn
            if end_pn:
                end_pn_url = get_page_number_url(end_pn)
                end_pn = get_page_number_link(end_pn_url, end_pn) or end_pn
                page_string += f'pp. {pn}–{end_pn}'
            else:
                page_string += f'p. {pn}'

            # Replace the source's page string if it exists
            page_str_regex = re.compile(r'.+, (pp?\. <a .+>\d+<\/a>)$')
            match = page_str_regex.match(html)
            if match:
                _page_string = match.group(1)
                html = html.replace(_page_string, page_string)
            else:
                html += f', {page_string}'
        if self.source.attributees.exists():
            from quotes.models import Quote
            if isinstance(self.content_object, Quote):
                quote = self.content_object
                if quote.ordered_attributees != self.source.ordered_attributees:
                    _html = html
                    if not quote.citations.filter(position__lt=self.position).exists():
                        html = f'{quote.attributee_string or "Unknown person"}'
                        html += f', {quote.date_string}' if quote.date else ''
                        html += f', quoted in {_html}'
                    else:
                        prior_citations = quote.citations.filter(position__lt=self.position)
                        prior_citation = prior_citations.last()
                        if 'quoted in' not in str(prior_citation):
                            html = f'quoted in {_html}'
                        else:
                            html = f'also in {_html}'
        # TODO: Remove search icon so citations can be joined together with semicolons
        # if self.source_file_url:
        #     html += (
        #         f'<a href="{self.source_file_url}" class="display-source"'
        #         f' target="_blank" data-toggle="modal" data-target="#modal">'
        #         f'<i class="fas fa-search"></i>'
        #         f'</a>'
        #     )
        # elif self.source.url or self.source.container and self.source.container.url:
        #     link = self.source.url if self.source.url else self.source.container.url
        #     if self.page_number:
        #         if 'www.sacred-texts.com' in link:
        #             link += f'#page_{self.page_number}'
        #         elif 'josephsmithpapers.org' in link:
        #             link += f'/{self.page_number}'
        #     html += (
        #         f'<a href="{link}" target="_blank">'
        #         f'<i class="fas fa-search"></i>'
        #         f'</a>'
        #     )
        return mark_safe(f'<span class="citation">{html}</span>')

    @property
    def number(self):
        return self.position + 1

    @property
    def source_file_page_number(self) -> Optional[int]:
        file = self.source.file
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
            elif hasattr(self.source, 'file_page_number'):
                return self.source.file_page_number
        return None

    @property
    def source_file_url(self) -> Optional[str]:
        file_url = self.source.file_url
        if file_url and self.source_file_page_number:
            if 'page=' in file_url:
                file_url = re.sub(r'page=\d+', f'page={self.source_file_page_number}', file_url)
            else:
                file_url = file_url + f'#page={self.source_file_page_number}'
        return file_url

    def clean(self):
        if self.end_page_number and self.end_page_number < self.page_number:
            raise ValidationError('The end page number must be greater than the start page number.')
