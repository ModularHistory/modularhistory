"""Model class for citations."""

import logging
import re
from typing import TYPE_CHECKING, Optional, Union

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.sources.serializers import CitationSerializer
from modularhistory.constants.content_types import ContentTypes, get_ct_id
from modularhistory.fields.html_field import (
    APPENDAGE_GROUP,
    END_PATTERN,
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
)
from modularhistory.fields.html_field import (
    PlaceholderGroups as DefaultPlaceholderGroups,
)
from modularhistory.models.positioned_relation import PositionedRelation
from modularhistory.utils import pdf
from modularhistory.utils.html import (
    components_to_html,
    compose_link,
    escape_quotes,
    soupify,
)

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

    from apps.quotes.models import Quote
    from apps.sources.models import PageRange


class PlaceholderGroups(DefaultPlaceholderGroups):
    """Group numbers for placeholder regex."""

    PAGE_STRING = 'page_string'
    # quotation (e.g., "It followed institutionalized procedures....")
    QUOTATION = 'quotation'


PAGE_STRING_GROUP = rf'(?P<{PlaceholderGroups.PAGE_STRING}>pp?\.\ [\d]+)'
QUOTATION_GROUP = rf'(?P<{PlaceholderGroups.QUOTATION}>\".+?\")'
HTML_GROUP = rf'(?P<{PlaceholderGroups.HTML}>\S.+?)'
citation_placeholder_pattern = rf'\ ?{OBJECT_PLACEHOLDER_REGEX}'.replace(
    APPENDAGE_GROUP,
    rf'(,\ {PAGE_STRING_GROUP})?(,\ {QUOTATION_GROUP})?(:?\ ?(?:<span style="display: none;?">|<span class="citation-placeholder">){HTML_GROUP}<\/span>)',  # noqa: E501'
).replace(TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>citation)')
logging.debug(f'Citation placeholder pattern: {citation_placeholder_pattern}')

PAGE_STRING_REGEX = r'.+, (pp?\. <a .+>\d+<\/a>)$'

SOURCE_TYPES = (('P', 'Primary'), ('S', 'Secondary'), ('T', 'Tertiary'))
CITATION_PHRASE_OPTIONS = (
    (None, ''),
    ('quoted in', 'quoted in'),
    ('cited in', 'cited in'),
    ('partially reproduced in', 'partially reproduced in'),
)
CITATION_PHRASE_MAX_LENGTH: int = 25


class Citation(PositionedRelation):
    """A reference to a source (from any other model)."""

    citation_phrase = models.CharField(
        max_length=CITATION_PHRASE_MAX_LENGTH,
        choices=CITATION_PHRASE_OPTIONS,
        default=None,
        null=True,
        blank=True,
    )
    source = models.ForeignKey(
        to='sources.Source',
        related_name='citations',
        on_delete=models.PROTECT,
    )
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    pages: 'RelatedManager[PageRange]'

    class Meta:
        unique_together = ['source', 'content_type', 'object_id', 'position']
        ordering = ['position', 'source']

    page_string_regex = re.compile(PAGE_STRING_REGEX)
    placeholder_regex = citation_placeholder_pattern
    serializer = CitationSerializer

    def __str__(self) -> str:
        """Return the citation's string representation."""
        return soupify(self.html).get_text()

    # TODO: refactor
    @property  # type: ignore
    def html(self) -> SafeString:
        """Return the citation's HTML representation."""
        html = f'{self.source.html}'
        if self.primary_page_number:
            page_string = self.page_number_html or ''
            # Replace the source's page string if it exists
            match = self.page_string_regex.match(html)
            if match:
                default_page_string = match.group(1)
                html = html.replace(default_page_string, page_string)
            else:
                html = f'{html}, {page_string}'
        if self.pk and self.source.attributees.exists():
            if self.content_type_id == get_ct_id(ContentTypes.quote):
                quote: Quote = self.content_object  # type: ignore
                if quote.ordered_attributees != self.source.ordered_attributees:
                    source_html = html
                    if quote.citations.filter(position__lt=self.position).exists():
                        prior_citations = quote.citations.filter(
                            position__lt=self.position
                        )
                        prior_citation = prior_citations.last()
                        if 'quoted in' not in str(prior_citation):
                            html = f'quoted in {source_html}'
                        else:
                            html = f'also in {source_html}'
                    else:
                        html = components_to_html(
                            [
                                f'{quote.attributee_html or "Unidentified person"}',
                                f'{quote.date_string}' if quote.date else '',
                                f'quoted in {source_html}',
                            ]
                        )
        # TODO: Remove search icon so citations can be joined together with semicolons
        the_following_code_is_fixed = False
        if the_following_code_is_fixed:
            if self.source_file:
                html += (
                    f'<a href="{self.source_file.url}" class="display-source"'
                    f' target="_blank" data-toggle="modal" data-target="#modal">'
                    f'<i class="fas fa-search"></i>'
                    f'</a>'
                )
            elif (
                self.source.url
                or self.source.containment
                and self.source.containment.container.url
            ):
                link = self.source.url or self.source.containment.container.url
                if self.page_number:
                    if 'www.sacred-texts.com' in link:
                        link = f'{link}#page_{self.page_number}'
                    elif 'josephsmithpapers.org' in link:
                        link = f'{link}/{self.page_number}'
                html += (
                    f'<a href="{link}" target="_blank">'
                    f'<i class="fas fa-search"></i>'
                    f'</a>'
                )
        html = f'<span class="citation">{html}</span>'
        return format_html(html)

    @property
    def number(self):
        """Return the citation's 1-based index."""
        return self.position + 1

    @property
    def primary_page_number(self) -> Optional[int]:
        """Return the page number of the citation's primary page range."""
        try:
            return self.pages.first().page_number  # type: ignore
        except (ObjectDoesNotExist, AttributeError):
            return None

    @property
    def page_number_html(self) -> Optional[str]:
        """Return the HTML representation of the citation's page numbers."""
        html = None
        page_number_strings = [
            page_range.unprefixed_html for page_range in self.pages.all().iterator()
        ]
        n_strings = len(page_number_strings)
        if n_strings > 1:
            html = f'pp. {", ".join(page_number_strings)}'
        elif n_strings:
            if re.search(r'(?:–|&ndash;)', page_number_strings[0]):
                html = f'pp. {", ".join(page_number_strings)}'
            else:
                html = f'p. {", ".join(page_number_strings)}'
        return html

    @property
    def source_file_page_number(self) -> Optional[int]:
        """Return the page number of the citation's source file."""
        file = self.source.source_file
        if file:
            if self.primary_page_number:
                return self.primary_page_number + file.page_offset
            elif getattr(self.source, 'file_page_number', None):
                return self.source.file_page_number
        return None

    @property
    def source_file_url(self) -> Optional[str]:
        """Return the URL of the citation's source file."""
        file_url = None
        if self.source.source_file:
            file_url = self.source.source_file.url
            if file_url and self.source_file_page_number:
                if pdf.url_specifies_page(file_url):
                    pattern = rf'{pdf.PAGE_KEY}=\d+'
                    replacement = f'{pdf.PAGE_KEY}={self.source_file_page_number}'
                    file_url = re.sub(pattern, replacement, file_url)
                else:
                    file_url = (
                        f'{file_url}#{pdf.PAGE_KEY}={self.source_file_page_number}'
                    )
        return file_url

    def get_page_number_url(self, page_number: Union[str, int]) -> Optional[str]:
        """Return a URL to a specific page of the citation's source file."""
        page_number = int(page_number)
        try:
            source_file = self.source.source_file
        except (AttributeError, ObjectDoesNotExist):
            return None
        if source_file:
            file_url = source_file.url
            if not file_url:
                return None
            page_number += source_file.page_offset
            if pdf.url_specifies_page(file_url):
                page_number_url = re.sub(
                    rf'{pdf.PAGE_KEY}=\d+', f'{pdf.PAGE_KEY}={page_number}', file_url
                )
            else:
                page_number_url = f'{file_url}#page={page_number}'
            return page_number_url
        return None

    def get_page_number_link(
        self, page_number: Union[str, int], url: Optional[str] = None
    ) -> Optional[str]:
        """Return a page number link string based on page_number."""
        url = url or self.get_page_number_url(page_number)
        if not url:
            return None
        return compose_link(
            page_number, href=url, klass='display-source', target='_blank'
        )

    @classmethod
    def get_object_html(
        cls, match: re.Match, use_preretrieved_html: bool = False
    ) -> Optional[str]:
        """Return the object's HTML based on a placeholder in the admin."""
        if not re.match(citation_placeholder_pattern, match.group(0)):
            raise ValueError(f'{match} does not match {citation_placeholder_pattern}')
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return preretrieved_html.strip()
        key = match.group(PlaceholderGroups.PK).strip()
        try:
            citation = cls.objects.get(pk=key)
        except ObjectDoesNotExist:
            logging.error(f'Unable to retrieve citation: {key}')
            return None
        source_string = str(citation)
        page_string = match.group(PlaceholderGroups.PAGE_STRING)
        quotation = match.group(PlaceholderGroups.QUOTATION)
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
        citation_link = compose_link(
            f'{citation.number}',
            href=f'#citation-{citation.pk}',
            klass='citation-link',
            title=escape_quotes(source_string),
        )
        citation_link = f'<sup>[{citation_link}]</sup>'
        logging.info(f'Composed citation link: {citation_link}')
        return citation_link

    @classmethod
    def get_updated_placeholder(cls, match: re.Match) -> str:
        """Return an up-to-date placeholder for a citation included in an HTML field."""
        placeholder = match.group(0)
        appendage = match.group(7)
        updated_appendage = (
            f'<span class="citation-placeholder">{cls.get_object_html(match)}</span>'
        )
        if appendage:
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            stem = re.sub(rf' ?{END_PATTERN}', '', placeholder)
            updated_placeholder = f'{stem}{updated_appendage} ]]'
        return updated_placeholder
