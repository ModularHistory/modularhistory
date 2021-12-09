"""Model class for citations."""

import logging
from typing import TYPE_CHECKING, Match, Optional, Union

import regex
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString

from core.fields.html_field import (
    APPENDAGE_GROUP,
    END_PATTERN,
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
)
from core.fields.html_field import PlaceholderGroups as DefaultPlaceholderGroups
from core.fields.json_field import JSONField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.relations.moderated import ModeratedPositionedRelation
from core.utils import pdf
from core.utils.html import components_to_html, compose_link, escape_quotes, soupify

if TYPE_CHECKING:
    from apps.quotes.models.quote import Quote


class PlaceholderGroups(DefaultPlaceholderGroups):
    """Group numbers for placeholder regex."""

    PAGE_STRING = 'page_string'
    # quotation (e.g., "It followed institutionalized procedures....")
    QUOTATION = 'quotation'


HYPHEN_OR_EN_DASH = r'\p{Pd}'
PAGE_STRING_GROUP = rf'(?P<{PlaceholderGroups.PAGE_STRING}>pp?\.\ [\d{HYPHEN_OR_EN_DASH}]+)'
QUOTATION_GROUP = rf'(?P<{PlaceholderGroups.QUOTATION}>\".+?\")'
HTML_GROUP = rf'(?P<{PlaceholderGroups.HTML}>\S.+?)'
citation_placeholder_pattern = rf'\ ?{OBJECT_PLACEHOLDER_REGEX}'.replace(
    APPENDAGE_GROUP,
    rf'(,\ {PAGE_STRING_GROUP})?(,\ {QUOTATION_GROUP})?(:?\ ?(?:<span style="display: none;?">|<span class="citation-placeholder">){HTML_GROUP}<\/span>)',  # noqa: E501'
).replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>citation)'
)  # noqa: WPS360

PAGE_STRING_REGEX = r'.+, (pp?\. <a .+>\d+<\/a>)$'

SOURCE_TYPES = (('P', 'Primary'), ('S', 'Secondary'), ('T', 'Tertiary'))
CITATION_PHRASE_OPTIONS = (
    (None, '-------'),
    ('quoted in', 'quoted in'),
    ('cited in', 'cited in'),
    ('partially reproduced in', 'partially reproduced in'),
)
CITATION_PHRASE_MAX_LENGTH: int = 25

# https://json-schema.org/understanding-json-schema/reference/array.html#tuple-validation
PAGES_SCHEMA = {
    'type': 'array',
    'items': {'$ref': '#/$definitions/page_range'},
    'uniqueItems': True,
    '$definitions': {
        'page_range': {
            'type': 'array',
            'items': [
                {'type': 'number'},  # start page number
                {'type': 'number'},  # end page number
            ],
            'additionalItems': False,
        }
    },
}


class AbstractCitation(ModeratedPositionedRelation):
    """Abstract base model for m2m relationships between sources and other models."""

    source = ManyToManyForeignKey(
        to='sources.Source',
        related_name='%(app_label)s_%(class)s_set',
    )
    # Foreign key to the model that references the source.
    content_object: models.ForeignKey
    citation_phrase = models.CharField(
        max_length=CITATION_PHRASE_MAX_LENGTH,
        choices=CITATION_PHRASE_OPTIONS,
        default=None,
        blank=True,
    )
    citation_html = models.TextField(blank=True)
    pages = JSONField(schema=PAGES_SCHEMA, default=list)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'content_object', 'position'],
                name='%(app_label)s_%(class)s_unique_positions',
            )
        ]

    page_string_regex = regex.compile(PAGE_STRING_REGEX)
    placeholder_regex = citation_placeholder_pattern

    @classmethod
    def get_serializer(cls):
        """Return the serializer for the citation."""
        return import_string(
            f'apps.{cls._meta.app_label}.api.serializers.{cls.__name__}Serializer'
        )

    def __str__(self) -> str:
        """Return the citation's string representation."""
        try:
            return soupify(self.citation_html).get_text()
        except Exception:
            return f'citation {self.pk}'

    @property
    def escaped_citation_html(self) -> SafeString:
        """Return the citation HTML, escaped."""
        return format_html(self.citation_html)

    # TODO: refactor
    @property  # type: ignore
    def html(self) -> SafeString:
        """Return the citation's HTML representation."""
        html = f'{self.source.citation_html}'
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
            if getattr(self.content_object, 'attributees', None):
                # Assume the content object is a quote.
                quote: Quote = self.content_object
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
                        html = components_to_html(
                            [
                                f'{quote.attributee_html or "Unidentified person"}',
                                f'{quote.date_string}' if quote.date else '',
                                f'quoted in {source_html}',
                            ]
                        )
        html = f'<span class="citation">{html}</span>'
        return format_html(html)

    @property
    def primary_page_number(self) -> Optional[int]:
        """Return the page number of the citation's primary page range."""
        try:
            return self.pages[0][0]
        except (IndexError, KeyError):
            return None

    @property
    def page_number_html(self) -> Optional[str]:
        """Return the HTML representation of the citation's page numbers."""
        html = None
        page_number_strings = []
        for page_range in self.pages:
            pn, end_pn = page_range[0], page_range[1] if len(page_range) > 1 else None
            pn_url = self.get_page_number_url(pn)
            pn_html = self.get_page_number_link(pn, pn_url) or str(pn)
            if end_pn:
                end_pn_url = self.get_page_number_url(end_pn)
                end_pn_html = self.get_page_number_link(end_pn, end_pn_url) or str(end_pn)
                pn_html = f'{pn_html}–{end_pn_html}'
            else:
                pn_html = f'{pn_html}'
            page_number_strings.append(pn_html)
        n_strings = len(page_number_strings)
        if n_strings == 1:
            page_number_string = page_number_strings[0]
            # Match any dash or hyphen.
            if regex.search(r'\p{Pd}', page_number_string):
                html = f'pp. {page_number_string}'
            else:
                html = f'p. {page_number_string}'
        elif n_strings:
            html = f'pp. {", ".join(page_number_strings)}'
        return html

    @property
    def source_file_page_number(self) -> Optional[int]:
        """Return the page number of the citation's source file."""
        file = self.source.file
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
        if self.source.file:
            file_url = self.source.file.url
            if file_url and self.source_file_page_number:
                if pdf.url_specifies_page(file_url):
                    pattern = rf'{pdf.PAGE_KEY}=\d+'
                    replacement = f'{pdf.PAGE_KEY}={self.source_file_page_number}'
                    file_url = regex.sub(pattern, replacement, file_url)
                else:
                    file_url = f'{file_url}#{pdf.PAGE_KEY}={self.source_file_page_number}'
        return file_url

    def get_page_number_url(self, page_number: Union[str, int]) -> Optional[str]:
        """Return a URL to a specific page of the citation's source file."""
        page_number = int(page_number)
        try:
            source_file = self.source.file
        except (AttributeError, ObjectDoesNotExist):
            return None
        if source_file:
            file_url = source_file.url
            if not file_url:
                return None
            page_number += source_file.page_offset
            if pdf.url_specifies_page(file_url):
                page_number_url = regex.sub(
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
        return compose_link(page_number, href=url, klass='display-source', target='_blank')

    @classmethod
    def get_object_html(cls, match: Match, use_preretrieved_html: bool = False) -> str:
        """Return the object's HTML based on a placeholder in the admin."""
        if not regex.match(citation_placeholder_pattern, match.group(0)):
            raise ValueError(f'{match} does not match {citation_placeholder_pattern}')
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return str(preretrieved_html).strip()
        key = match.group(PlaceholderGroups.PK).strip()
        try:
            citation = cls.objects.get(pk=key)
        except ObjectDoesNotExist:
            logging.error(f'Unable to retrieve citation: {key}')
            return ''
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
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return an up-to-date placeholder for a citation included in an HTML field."""
        placeholder = match.group(0)
        appendage = match.group(7)
        updated_appendage = (
            f'<span class="citation-placeholder">{cls.get_object_html(match)}</span>'
        )
        if appendage:
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            stem = regex.sub(rf' ?{END_PATTERN}', '', placeholder)  # noqa: WPS360
            updated_placeholder = f'{stem}{updated_appendage} ]]'
        return updated_placeholder
