"""Model classes for sources."""

import logging
import re
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Union

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _
from gm2m import GM2MField as GenericManyToManyField
from polymorphic.models import PolymorphicModel

from apps.entities.models.model_with_related_entities import ModelWithRelatedEntities
from apps.search.models import SearchableDatedModel
from apps.sources.manager import PolymorphicSourceManager
from apps.sources.models.source_file import SourceFile
from apps.sources.serializers import SourceSerializer
from modularhistory.fields import HistoricDateTimeField, HTMLField, JSONField
from modularhistory.models import TypedModel, retrieve_or_compute
from modularhistory.structures.historic_datetime import HistoricDateTime
from modularhistory.utils.html import NEW_TAB, components_to_html, compose_link, soupify
from modularhistory.utils.string import fix_comma_positions

if TYPE_CHECKING:
    from apps.entities.models import Entity
    from apps.sources.models.source_containment import SourceContainment

MAX_CITATION_STRING_LENGTH: int = 500
MAX_CITATION_HTML_LENGTH: int = 1000
MAX_URL_LENGTH: int = 100
MAX_ATTRIBUTEE_HTML_LENGTH: int = 300
MAX_ATTRIBUTEE_STRING_LENGTH: int = 100
MAX_TITLE_LENGTH: int = 250

COMPONENT_DELIMITER = ', '

SOURCE_TYPES = (('P', 'Primary'), ('S', 'Secondary'), ('T', 'Tertiary'))

CITATION_PHRASE_OPTIONS = (
    (None, ''),
    ('quoted in', 'quoted in'),
    ('cited in', 'cited in'),
)


class PolymorphicSource(
    PolymorphicModel, SearchableDatedModel, ModelWithRelatedEntities
):
    """A source of content or information."""

    attributee_html = models.CharField(
        max_length=MAX_ATTRIBUTEE_HTML_LENGTH, null=True, blank=True
    )
    attributee_string = models.CharField(
        max_length=MAX_ATTRIBUTEE_STRING_LENGTH, null=True, blank=True
    )
    attributees = models.ManyToManyField(
        to='entities.Entity',
        through='SourceAttribution',
        related_name='attributed_sources',
        # Some sources may not have attributees.
    )
    citation_html = models.TextField(null=False, blank=True)
    citation_string = models.CharField(
        max_length=MAX_CITATION_STRING_LENGTH,
        null=False,
        blank=True,
        unique=True,
    )
    containers = models.ManyToManyField(
        to='self',
        through='sources.SourceContainment',
        through_fields=('source', 'container'),
        related_name='contained_sources',
        symmetrical=False,
        blank=True,
    )
    date = HistoricDateTimeField(null=True, blank=True)
    description = HTMLField(null=True, blank=True, paragraphed=True)
    file = models.ForeignKey(
        to=SourceFile,
        related_name='polymorphic_sources',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='file',
    )
    location = models.ForeignKey(
        to='places.Place', null=True, blank=True, on_delete=models.SET_NULL
    )
    publication_date = HistoricDateTimeField(null=True, blank=True)
    related = GenericManyToManyField(
        'quotes.Quote',
        'occurrences.Occurrence',
        through='sources.Citation',
        related_name='sources',
        blank=True,
    )
    title = models.CharField(
        verbose_name=_('title'), max_length=MAX_TITLE_LENGTH, null=True, blank=True
    )
    url = models.URLField(
        max_length=MAX_URL_LENGTH,
        null=True,
        blank=True,
        help_text='URL where the source can be accessed online',
    )

    class Meta:
        ordering = ['-date']

    objects = PolymorphicSourceManager()
    searchable_fields = ['citation_string', 'description']
    serializer = SourceSerializer
    slug_base_field = 'title'

    def __str__(self):
        """Return the source's string representation."""
        return self.citation_string

    def clean(self):
        """Prepare the source to be saved."""
        super().clean()
        self.citation_html = self.calculate_citation_html()
        self.citation_string = soupify(self.citation_html).get_text()
        if not self.file:
            if self.containment and self.containment.container.file:
                self.file = self.containment.container.file
        if self.pk:  # If this source is not being newly created
            is_duplicate = (
                PolymorphicSource.objects.exclude(pk=self.pk)
                .filter(citation_string=self.citation_string)
                .exists()
            )
            if is_duplicate:
                raise ValidationError(
                    f'Unable to save this source because it duplicates an existing source '
                    f'or has an identical string: {self.citation_string}'
                )
            for container in self.containers.all():
                if self in container.containers.all():
                    raise ValidationError(
                        f'This source cannot be contained by {container}, '
                        f'because that source is already contained by this source.'
                    )

    @property
    def admin_source_link(self) -> SafeString:
        """Return a file link to display in the admin."""
        element = ''
        if self.file:
            element = compose_link(
                '<i class="fa fa-search"></i>',
                href=self.url,
                klass='btn btn-small btn-default display-source',
                target=NEW_TAB,
            )
        return format_html(element)

    @property
    def ctype(self):
        return self.polymorphic_ctype

    @property
    def escaped_citation_html(self) -> SafeString:
        return format_html(self.citation_html)

    @property
    def calculate_attributee_html(self) -> Optional[str]:
        """Return an HTML string representing the source's attributees."""
        # Check for pk to avoid RecursionErrors with not-yet-saved objects
        has_attributees = self.attributees.exists() if self.pk else False
        if self.attributee_string:
            attributee_html = self.attributee_string
            if has_attributees:
                for entity in self.attributees.all().iterator():
                    if entity.name in attributee_html:
                        attributee_html = attributee_html.replace(
                            entity.name, entity.name_html
                        )
            else:
                logging.info(f'Returning preset creator string: {attributee_html}')
            return format_html(attributee_html)
        elif not has_attributees:
            return None
        attributees = self.ordered_attributees
        n_attributions = len(attributees)
        first_attributee = attributees[0]
        html = first_attributee.name_html
        if n_attributions == 2:
            html = f'{html} and {attributees[1].name_html}'
        elif n_attributions == 3:
            html = f'{html}, {attributees[1].name_html}, and {attributees[2].name_html}'
        elif n_attributions > 3:
            html = f'{html} et al.'
        return html

    def calculate_citation_html(self) -> str:
        """Return the HTML representation of the source, including its containers."""
        # TODO: html methods should be split into different classes and/or mixins.
        html = self.__html__()
        container_strings = self.get_container_strings()
        if container_strings:
            containers = ', and '.join(container_strings)
            html = f'{html}, {containers}'
        elif getattr(self, 'page_number', None):
            page_number_html = _get_page_number_html(
                self, self.source_file, self.page_number, self.end_page_number
            )
            html = f'{html}, {page_number_html}'
        if not self.source_file:
            if self.link and self.link not in html:
                html = f'{html}, retrieved from {self.link}'
        if getattr(self, 'information_url', None) and self.information_url:
            html = (
                f'{html}, information available at '
                f'{compose_link(self.information_url, href=self.information_url, target="_blank")}'
            )
        the_code_below_is_good = False
        if the_code_below_is_good:
            # TODO: Remove search icon; insert link intelligently
            if self.file_url:
                html += (
                    f'<a href="{self.file_url}" class="mx-1 display-source"'
                    f' data-toggle="modal" data-target="#modal">'
                    f'<i class="fas fa-search"></i>'
                    f'</a>'
                )
            elif self.url:
                link = self.url
                if self.page_number and 'www.sacred-texts.com' in link:
                    link = f'{link}#page_{self.page_number}'
                html += (
                    f'<a href="{link}" class="mx-1" target="_blank">'
                    f'<i class="fas fa-search"></i>'
                    f'</a>'
                )
        return format_html(fix_comma_positions(html))

    @property
    def containment(self) -> Optional['SourceContainment']:
        """Return the source's primary containment."""
        try:
            return self.source_containments.first()
        except (ObjectDoesNotExist, AttributeError):
            return None

    @property
    def escaped_citation_html(self) -> SafeString:
        return format_html(self.citation_html)

    def get_container_strings(self) -> Optional[List[str]]:
        """Return a list of strings representing the source's containers."""
        containments = self.source_containments.order_by('position')[:2]
        container_strings = []
        same_creator = True
        for containment in containments:
            container_html = f'{containment.container.html}'

            # Determine whether the container has the same attributee
            if containment.container.attributee_html != self.attributee_html:
                same_creator = False

            # Remove redundant creator string if necessary
            creator_string_is_duplicated = (
                same_creator
                and self.attributee_html
                and self.attributee_html in container_html
            )
            if creator_string_is_duplicated:
                container_html = container_html[len(f'{self.attributee_html}, ') :]

            # Include the page number
            if containment.page_number:
                page_number_html = _get_page_number_html(
                    containment.source,
                    containment.source.source_file,
                    containment.page_number,
                    containment.end_page_number,
                )
                container_html = f'{container_html}, {page_number_html}'
            container_html = (
                f'{containment.phrase} in {container_html}'
                if containment.phrase
                else f'in {container_html}'
            )
            container_strings.append(container_html)
        return container_strings

    def get_date(self) -> Optional[HistoricDateTime]:
        """Get the source's date."""  # TODO: prefetch container?
        if self.date:
            return self.date
        elif self.containment and self.containment.container.date:
            return self.containment.container.date
        return None

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='href')
    def href(self) -> Optional[str]:
        """
        Return the href to use when providing a link to the source.

        If the source has a file, the URL of the file is returned;
        otherwise, the source's `url` field value is returned.
        """
        if self.source_file_url:
            url = self.source_file_url
            page_number = self.source_file.default_page_number
            if getattr(self, 'page_number', None):
                page_number = self.page_number + self.source_file.page_offset
            if page_number:
                url = _set_page_number(url, page_number)
        else:
            url = self.url
        return url

    @property
    def link(self) -> Optional[SafeString]:
        """Return an HTML link element containing the source URL, if one exists."""
        if self.url:
            return format_html(f'<a target="_blank" href="{self.url}">{self.url}</a>')
        return None

    @property
    def linked_title(self) -> Optional[SafeString]:
        """Return the source's title as a link."""
        if not self.title:
            return None
        html = (
            compose_link(
                self.title,
                href=self.href,
                klass='source-title display-source',
                target=NEW_TAB,
            )
            if self.href
            else self.title
        )
        return format_html(html)

    @property
    def ordered_attributees(self) -> List['Entity']:
        """Return an ordered list of the source's attributees."""
        try:
            attributions = self.attributions.select_related('attributee')
            return [attribution.attributee for attribution in attributions]
        except (AttributeError, ObjectDoesNotExist):
            return []

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='containers')
    def serialized_containments(self) -> List[Dict]:
        """Return the source's containers, serialized."""
        return [
            containment.container.serialize()
            for containment in self.source_containments.all().select_related(
                'container'
            )
        ]

    @property
    def source_file_url(self) -> Optional[str]:
        """Return the source file's URL, if it has one."""
        return self.source_file.url if self.source_file else None

    def __html__(self) -> str:
        """
        Return the source's HTML representation, not including its containers.

        Must be defined by models inheriting from Source.
        """
        raise NotImplementedError

    @staticmethod
    def components_to_html(components: Sequence[Optional[str]]):
        """Combine a list of HTML components into an HTML string."""
        return components_to_html(components, delimiter=COMPONENT_DELIMITER)


def _get_page_number_url(
    source: PolymorphicSource, file: SourceFile, page_number: int
) -> Optional[str]:
    """TODO: write docstring."""
    url = source.source_file_url or None
    if not url:
        return None
    page_number += file.page_offset
    return _set_page_number(url, page_number)


def _get_page_number_link(url: str, page_number: int) -> Optional[str]:
    """TODO: write docstring."""
    if not url:
        return None
    return compose_link(page_number, href=url, klass='display-source', target=NEW_TAB)


def _get_page_number_html(
    source: PolymorphicSource,
    file: Optional[SourceFile],
    page_number: int,
    end_page_number: Optional[int] = None,
) -> str:
    """TODO: write docstring."""
    pn_url = _get_page_number_url(source=source, file=file, page_number=page_number)
    pn = _get_page_number_link(url=pn_url, page_number=page_number) or page_number
    if end_page_number:
        end_pn_url = _get_page_number_url(
            source=source, file=file, page_number=end_page_number
        )
        end_pn = (
            _get_page_number_link(url=end_pn_url, page_number=end_page_number)
            or end_page_number
        )
        return f'pp. {pn}–{end_pn}'
    return f'p. {pn}'


def _set_page_number(url: str, page_number: Union[str, int]) -> str:
    page_param = 'page'
    if f'{page_param}=' in url:
        url = re.sub(rf'{page_param}=\d+', f'{page_param}={page_number}', url)
    else:
        url = f'{url}#{page_param}={page_number}'
    return url


class Source(TypedModel, SearchableDatedModel, ModelWithRelatedEntities):
    """A source for quotes or historical information."""

    full_string = models.CharField(
        verbose_name='searchable string',
        max_length=MAX_CITATION_STRING_LENGTH,
        null=False,
        blank=True,
        unique=True,
    )
    title = models.CharField(
        verbose_name=_('title'), max_length=MAX_TITLE_LENGTH, null=True, blank=True
    )
    url = models.URLField(
        max_length=MAX_URL_LENGTH,
        null=True,
        blank=True,
        help_text='URL where the source can be accessed online',
    )
    description = HTMLField(null=True, blank=True, paragraphed=True)
    date = HistoricDateTimeField(null=True, blank=True)
    publication_date = HistoricDateTimeField(null=True, blank=True)
    location = models.ForeignKey(
        to='places.Place', null=True, blank=True, on_delete=models.SET_NULL
    )
    db_file = models.ForeignKey(
        to=SourceFile,
        related_name='sources',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='file',
    )
    creators = models.CharField(
        max_length=MAX_ATTRIBUTEE_STRING_LENGTH, null=True, blank=True
    )
    # TODO: make many to many
    collection = models.ForeignKey(
        to='sources.Collection',
        related_name='documents',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    publication = models.ForeignKey(
        'sources.Publication', null=True, blank=True, on_delete=models.CASCADE
    )

    extra = JSONField(null=True, blank=True, default=dict, schema='extra_field_schema')

    class Meta:
        ordering = ['creators', '-date']

    class FieldNames(SearchableDatedModel.FieldNames):
        collection = 'collection'
        creators = 'creators'
        description = 'description'
        extra = 'extra'
        file = 'db_file'
        location = 'location'
        publication = 'publication'
        related = 'related'
        string = 'full_string'
        title = 'title'
        type = 'type'
        url = 'url'

    extra_field_schema: Dict[str, str] = {}
    inapplicable_fields: List[str] = []
    searchable_fields = [FieldNames.string, FieldNames.description]
    serializer = SourceSerializer
    slug_base_field = 'title'

    def __str__(self):
        """Return the source's string representation."""
        return soupify(self.html).get_text()  # type: ignore

    def save(self, *args, **kwargs):
        """Save the source."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Prepare the source to be saved."""
        logging.debug(f'Cleaning source ({self.type})...')
        super().clean()
        if self.type == 'sources.source' or not self.type:
            raise ValidationError('Source must have a type.')
        else:
            # Prevent a RuntimeError when saving a new source
            self.recast(self.type)
        try:
            self.full_string = str(self)
        except Exception as err:
            logging.error(f'Attempt to save searchable source string resulted in {err}')
        if self.pk:  # If this source is not being newly created
            is_duplicate = (
                Source.objects.exclude(pk=self.pk)
                .filter(full_string=self.full_string)
                .exists()
            )
            if is_duplicate:
                raise ValidationError(
                    f'Unable to save this source because it duplicates an existing source '
                    f'or has an identical string: {self.full_string}'
                )
            for container in self.containers.all():
                if self in container.containers.all():
                    raise ValidationError(
                        f'This source cannot be contained by {container}, '
                        f'because that source is already contained by this source.'
                    )

    @property
    def admin_source_link(self) -> SafeString:
        """Return a file link to display in the admin."""
        element = ''
        if self.source_file:
            element = compose_link(
                '<i class="fa fa-search"></i>',
                href=self.href,
                klass='btn btn-small btn-default display-source',
                target=NEW_TAB,
            )
        return format_html(element)

    @property
    def attributee_html(self) -> Optional[str]:
        """Return an HTML string representing the source's attributees."""
        # Check for pk to avoid RecursionErrors with not-yet-saved objects
        has_attributees = self.attributees.exists() if self.pk else False
        if self.creators:
            attributee_html = self.creators
            if has_attributees:
                for entity in self.attributees.all().iterator():
                    if entity.name in attributee_html:
                        attributee_html = attributee_html.replace(
                            entity.name, entity.name_html
                        )
            else:
                logging.info(f'Returning preset creator string: {attributee_html}')
            return format_html(attributee_html)
        elif not has_attributees:
            return None
        attributees = self.ordered_attributees
        n_attributions = len(attributees)
        first_attributee = attributees[0]
        html = first_attributee.name_html
        if n_attributions == 2:
            html = f'{html} and {attributees[1].name_html}'
        elif n_attributions == 3:
            html = f'{html}, {attributees[1].name_html}, and {attributees[2].name_html}'
        elif n_attributions > 3:
            html = f'{html} et al.'
        return html

    @property
    def attributee_string(self) -> Optional[str]:
        """Return a string representing the source's attributees."""
        if self.attributee_html:
            return soupify(self.attributee_html).get_text()
        return None

    @property
    def containment(self) -> Optional['SourceContainment']:
        """Return the source's primary containment."""
        try:
            return self.source_containments.first()
        except (ObjectDoesNotExist, AttributeError):
            return None

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='containers')
    def serialized_containments(self) -> List[Dict]:
        """Return the source's containers, serialized."""
        return [
            containment.container.serialize()
            for containment in self.source_containments.all().select_related(
                'container'
            )
        ]

    @property
    def source_file(self) -> Optional[SourceFile]:
        """Return the source's file, if it has one."""
        if self.db_file:
            return self.db_file
        # TODO: save container file as source file?
        return self.containment.container.db_file if self.containment else None

    @source_file.setter
    def source_file(self, value):
        """Setter for source_file."""
        self.db_file = value

    @property
    def source_file_url(self) -> Optional[str]:
        """Return the source file's URL, if it has one."""
        return self.source_file.url if self.source_file else None

    def get_container_strings(self) -> Optional[List[str]]:
        """Return a list of strings representing the source's containers."""
        containments = self.source_containments.order_by('position')[:2]
        container_strings = []
        same_creator = True
        for containment in containments:
            container_html = f'{containment.container.html}'

            # Determine whether the container has the same attributee
            if containment.container.attributee_html != self.attributee_html:
                same_creator = False

            # Remove redundant creator string if necessary
            creator_string_is_duplicated = (
                same_creator
                and self.attributee_html
                and self.attributee_html in container_html
            )
            if creator_string_is_duplicated:
                container_html = container_html[len(f'{self.attributee_html}, ') :]

            # Include the page number
            if containment.page_number:
                page_number_html = _get_page_number_html(
                    containment.source,
                    containment.source.source_file,
                    containment.page_number,
                    containment.end_page_number,
                )
                container_html = f'{container_html}, {page_number_html}'
            container_html = (
                f'{containment.phrase} in {container_html}'
                if containment.phrase
                else f'in {container_html}'
            )
            container_strings.append(container_html)
        return container_strings

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='href')
    def href(self) -> Optional[str]:
        """
        Return the href to use when providing a link to the source.

        If the source has a file, the URL of the file is returned;
        otherwise, the source's `url` field value is returned.
        """
        if self.source_file_url:
            url = self.source_file_url
            page_number = self.source_file.default_page_number
            if getattr(self, 'page_number', None):
                page_number = self.page_number + self.source_file.page_offset
            if page_number:
                url = _set_page_number(url, page_number)
        else:
            url = self.url
        return url

    # Note: This method is subsequently transformed into a property.
    @retrieve_or_compute(attribute_name='html', caster=format_html)
    def html(self) -> SafeString:
        """
        Return the HTML representation of the source, including its containers.

        This method is accessible as a property.
        """
        # TODO: html methods should be split into different classes and/or mixins.
        html = self.__html__()
        container_strings = self.get_container_strings()
        if container_strings:
            containers = ', and '.join(container_strings)
            html = f'{html}, {containers}'
        elif getattr(self, 'page_number', None):
            page_number_html = _get_page_number_html(
                self, self.source_file, self.page_number, self.end_page_number
            )
            html = f'{html}, {page_number_html}'
        if not self.source_file:
            if self.link and self.link not in html:
                html = f'{html}, retrieved from {self.link}'
        if getattr(self, 'information_url', None) and self.information_url:
            html = (
                f'{html}, information available at '
                f'{compose_link(self.information_url, href=self.information_url, target="_blank")}'
            )
        the_code_below_is_good = False
        if the_code_below_is_good:
            # TODO: Remove search icon; insert link intelligently
            if self.file_url:
                html += (
                    f'<a href="{self.file_url}" class="mx-1 display-source"'
                    f' data-toggle="modal" data-target="#modal">'
                    f'<i class="fas fa-search"></i>'
                    f'</a>'
                )
            elif self.url:
                link = self.url
                if self.page_number and 'www.sacred-texts.com' in link:
                    link = f'{link}#page_{self.page_number}'
                html += (
                    f'<a href="{link}" class="mx-1" target="_blank">'
                    f'<i class="fas fa-search"></i>'
                    f'</a>'
                )
        return format_html(fix_comma_positions(html))

    html.admin_order_field = FieldNames.string
    html: SafeString = property(html)  # type: ignore

    @property
    def link(self) -> Optional[SafeString]:
        """Return an HTML link element containing the source URL, if one exists."""
        if self.url:
            return format_html(f'<a target="_blank" href="{self.url}">{self.url}</a>')
        return None

    @property
    def ordered_attributees(self) -> List['Entity']:
        """Return an ordered list of the source's attributees."""
        try:
            attributions = self.attributions.select_related('attributee')
            return [attribution.attributee for attribution in attributions]
        except (AttributeError, ObjectDoesNotExist):
            return []

    @property
    def string(self) -> str:
        """Return the source's string representation, including its containers."""
        return soupify(self.html).get_text()  # type: ignore

    @property
    def linked_title(self) -> Optional[SafeString]:
        """Return the source's title as a link."""
        if not self.title:
            return None
        html = (
            compose_link(
                self.title,
                href=self.href,
                klass='source-title display-source',
                target=NEW_TAB,
            )
            if self.href
            else self.title
        )
        return format_html(html)

    @staticmethod
    def components_to_html(components: Sequence[Optional[str]]):
        """Combine a list of HTML components into an HTML string."""
        return components_to_html(components, delimiter=COMPONENT_DELIMITER)

    def get_date(self) -> Optional[HistoricDateTime]:
        """Get the source's date."""  # TODO: prefetch container?
        if self.date:
            return self.date
        elif self.containment and self.containment.container.date:
            return self.containment.container.date
        return None

    def __html__(self) -> str:
        """
        Return the source's HTML representation, not including its containers.

        Must be defined by models inheriting from Source.
        """
        raise NotImplementedError
