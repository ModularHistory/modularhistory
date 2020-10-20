"""Model class for citations."""

import re
from sys import stderr
from typing import Any, Optional, TYPE_CHECKING, Union

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CASCADE, ForeignKey, PositiveSmallIntegerField, SET_NULL
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.constants import QUOTE_CT_ID, EMPTY_STRING
from modularhistory.models import Model
from modularhistory.utils.html import soupify, compose_link, components_to_html

if TYPE_CHECKING:
    from quotes.models import Quote

# group 1: citation pk (e.g., '988')
# group 2: ignore
# group 3: page string (e.g., 'p. 22')
# group 4: ignore
# group 5: quotation (e.g., "It followed institutionalized procedures....")
# group 6: ignore
# group 7: citation HTML
ADMIN_PLACEHOLDER_REGEX = (
    r'\ ?<<\ ?citation:\ ?([\d\w-]+)(,\ (pp?\.\ [\d]+))?(,\ (\".+?\"))?\ ?'
    r'(<span style="display: none;?">(.+)<\/span>)?\ ?>>'
)

PAGE_STRING_REGEX = r'.+, (pp?\. <a .+>\d+<\/a>)$'

SOURCE_TYPES = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
    ('T', 'Tertiary')
)

CITATION_PHRASE_OPTIONS = (
    (None, EMPTY_STRING),
    ('quoted in', 'quoted in'),
    ('cited in', 'cited in'),
    ('partially reproduced in', 'partially reproduced in')
)
CITATION_PHRASE_MAX_LENGTH: int = 25


class Citation(Model):
    """A reference to a source (from any other model)."""

    citation_phrase = models.CharField(
        max_length=CITATION_PHRASE_MAX_LENGTH,
        choices=CITATION_PHRASE_OPTIONS,
        default=None,
        null=True,
        blank=True
    )
    source = ForeignKey(
        'sources.Source',
        related_name='citations',
        on_delete=SET_NULL,
        null=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )

    pages: Any
    position = PositiveSmallIntegerField(
        null=True,
        blank=True,  # TODO: add cleaning logic
        help_text='Determines the order of references.'
    )

    class Meta:
        unique_together = ['source', 'content_type', 'object_id', 'position']
        ordering = ['position', 'source']

    admin_placeholder_regex = re.compile(ADMIN_PLACEHOLDER_REGEX)
    page_string_regex = re.compile(PAGE_STRING_REGEX)

    def __str__(self) -> str:
        """Returns the citation's string representation."""
        return soupify(self.html).get_text()

    @property
    def html(self) -> SafeString:
        """Returns the citation's HTML representation."""
        html = f'{self.source.html}'
        if self.primary_page_number:
            page_string = self.page_number_html or EMPTY_STRING
            # Replace the source's page string if it exists
            match = self.page_string_regex.match(html)
            if match:
                default_page_string = match.group(1)
                html = html.replace(default_page_string, page_string)
            else:
                html = f'{html}, {page_string}'
        if self.pk and self.source.attributees.exists():
            if self.content_type_id == QUOTE_CT_ID:
                quote: Quote = self.content_object  # type: ignore
                if quote.ordered_attributees != self.source.ordered_attributees:
                    source_html = html
                    if quote.citations.filter(position__lt=self.position).exists():
                        prior_citations = quote.citations.filter(position__lt=self.position)
                        prior_citation = prior_citations.last()
                        if 'quoted in' not in str(prior_citation):
                            html = f'quoted in {source_html}'
                        else:
                            html = f'also in {source_html}'
                    else:
                        html = components_to_html([
                            f'{quote.attributee_string or "Unidentified person"}',
                            f'{quote.date_string}' if quote.date else EMPTY_STRING,
                            f'quoted in {source_html}'
                        ])
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
        #             link = f'{link}#page_{self.page_number}'
        #         elif 'josephsmithpapers.org' in link:
        #             link = f'{link}/{self.page_number}'
        #     html += (
        #         f'<a href="{link}" target="_blank">'
        #         f'<i class="fas fa-search"></i>'
        #         f'</a>'
        #     )
        return format_html(f'<span class="citation">{html}</span>')

    @property
    def html_id(self) -> Optional[str]:
        """Returns the citation's HTML id."""
        if self.pk:
            return f'citation-{self.pk}'
        return None

    @property
    def number(self):
        """Returns the citation's 1-based index in its source's citation set."""
        return self.position + 1

    @property
    def primary_page_number(self) -> Optional[int]:
        """Returns the page number of the citation's primary page range."""
        try:
            return self.pages.first().page_number
        except (ObjectDoesNotExist, AttributeError):
            return None

    @property
    def page_number_html(self) -> Optional[str]:
        """Returns the HTML representation of the citation's page numbers."""
        page_number_strings = [page_range.html for page_range in self.pages.all()]
        if page_number_strings:
            return format_html(', '.join(page_number_strings))
        return None

    @property
    def source_file_page_number(self) -> Optional[int]:
        """Returns the page number of the citation's source file."""
        file = self.source.source_file
        if file:
            if self.primary_page_number:
                return self.primary_page_number + file.page_offset
            elif hasattr(self.source, 'file_page_number'):
                return self.source.file_page_number
        return None

    @property
    def source_file_url(self) -> Optional[str]:
        """Returns the URL of the citation's source file."""
        file_url = self.source.file_url
        if file_url and self.source_file_page_number:
            if 'page=' in file_url:
                file_url = re.sub(r'page=\d+', f'page={self.source_file_page_number}', file_url)
            else:
                file_url = f'{file_url}#page={self.source_file_page_number}'
        return file_url

    def get_page_number_url(self, page_number: Union[str, int]) -> Optional[str]:
        """Returns a URL to a specific page of the citation's source file."""
        page_number = int(page_number)
        file_url = self.source.file_url or None
        if not file_url:
            return None
        page_number += self.source.source_file.page_offset
        if 'page=' in file_url:
            page_number_url = re.sub(r'page=\d+', f'page={page_number}', file_url)
        else:
            page_number_url = f'{file_url}#page={page_number}'
        return page_number_url

    def get_page_number_link(
        self,
        page_number: Union[str, int],
        url: Optional[str] = None
    ) -> Optional[str]:
        """Returns a page number link string based on page_number."""
        url = url or self.get_page_number_url(page_number)
        if not url:
            return None
        return compose_link(page_number, href=url, klass='display-source', target='_blank')

    @classmethod
    def get_object_html(cls, match: re.Match, use_preretrieved_html: bool = False) -> Optional[str]:
        """Return the object's HTML based on a placeholder in the admin."""
        if not re.match(ADMIN_PLACEHOLDER_REGEX, match.group(0)):
            raise ValueError(f'{match} does not match {ADMIN_PLACEHOLDER_REGEX}')

        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(7)
            if preretrieved_html:
                return preretrieved_html.strip()

        key = match.group(1).strip()
        try:
            citation = cls.objects.get(pk=key)
        except ObjectDoesNotExist:
            print(f'Unable to retrieve citation: {key}', file=stderr)
            return None
        html_id = citation.html_id
        source_string = str(citation)
        page_string = match.group(3)
        quotation = match.group(5)
        if page_string:
            page_string = page_string.strip()
            page_str_match = cls.page_string_regex.match(source_string)
            if page_str_match:
                default_page_string = page_str_match.group(1)
                source_string = source_string.replace(default_page_string, page_string)
            else:
                source_string = f'{source_string}, {page_string}'
        if quotation:
            source_string = f'{source_string}: {quotation}'
        source_string = source_string.replace('"', '&quot;').replace("'", '&#39;')
        return compose_link(
            f'<sup>{citation.number}</sup>',
            href=f'#{html_id}',
            klass='citation-link',
            title=source_string
        )

    @classmethod
    def get_updated_placeholder(cls, match: re.Match) -> str:
        """Return an up-to-date placeholder for a citation included in an HTML field."""
        placeholder = match.group(0)
        appendage = match.group(6)
        updated_appendage = f'<span style="display: none">{cls.get_object_html(match)}</span>'
        if appendage:
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            updated_placeholder = (
                f'{placeholder.replace(" }}", "").replace("}}", "")}'
                f'{updated_appendage} >>'
            )
        return updated_placeholder
