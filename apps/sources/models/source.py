"""Model classes for sources."""

import logging
import re
from typing import TYPE_CHECKING, List, Optional, Sequence, Union

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.query import QuerySet
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _
from gm2m import GM2MField as GenericManyToManyField
from polymorphic.models import PolymorphicModel

from apps.dates.fields import HistoricDateTimeField
from apps.dates.structures import HistoricDateTime
from apps.entities.models.model_with_related_entities import ModelWithRelatedEntities
from apps.search.models import SearchableDatedModel
from apps.sources.manager import PolymorphicSourceManager, PolymorphicSourceQuerySet
from apps.sources.models.source_file import SourceFile
from apps.sources.serializers import SourceSerializer
from core.fields import HTMLField
from core.models import retrieve_or_compute
from core.utils.html import NEW_TAB, components_to_html, compose_link, soupify
from core.utils.string import fix_comma_positions

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


class Source(PolymorphicModel, SearchableDatedModel, ModelWithRelatedEntities):
    """A source of content or information."""

    citation_html = models.TextField(
        verbose_name=_('citation HTML'),
        null=False,
        # Allow to be blank in model forms (and calculated during cleaning).
        blank=True,
    )
    citation_string = models.CharField(
        verbose_name=_('citation string'),
        max_length=MAX_CITATION_STRING_LENGTH,
        null=False,
        # Allow to be blank in model forms (and calculated during cleaning).
        blank=True,
        unique=True,
    )
    attributee_html = models.CharField(
        max_length=MAX_ATTRIBUTEE_HTML_LENGTH,
        null=True,
        blank=True,
        verbose_name=_('attributee HTML'),
    )
    attributee_string = models.CharField(
        max_length=MAX_ATTRIBUTEE_STRING_LENGTH,
        null=True,
        blank=True,
        verbose_name=_('attributee string'),
    )
    attributees = models.ManyToManyField(
        to='entities.Entity',
        through='SourceAttribution',
        related_name='attributed_sources',
        blank=True,  # Some sources may not have attributees.
        verbose_name=_('attributees'),
    )
    containment_html = models.TextField(
        verbose_name=_('containment HTML'), null=True, blank=True
    )
    containers = models.ManyToManyField(
        to='self',
        through='sources.SourceContainment',
        through_fields=('source', 'container'),
        related_name='contained_sources',
        symmetrical=False,
        blank=True,
        verbose_name=_('containers'),
    )

    # `date` must be nullable at the db level (because some sources simply
    # do not have dates), but if no date is set, we use the `clean` method
    # to raise a ValidationError unless the child model whitelists itself
    # by setting `date_nullable` to True.
    date = HistoricDateTimeField(null=True, blank=True)
    # `date_nullable` can be set to True by child models that require the
    # date field to be nullable for any reason (e.g., by the Webpage model,
    # since not all webpages present their creation date, or by the Document
    # model, since some documents cannot be dated and/or are compilations of
    # material spanning decades).
    date_nullable: bool = False

    description = HTMLField(
        verbose_name=_('description'), null=True, blank=True, paragraphed=True
    )
    file = models.ForeignKey(
        to=SourceFile,
        related_name='sources',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='file',
    )
    href = models.URLField(
        verbose_name=_('href'),
        null=True,
        blank=True,
        help_text=(
            'URL to use as the href when presenting a link to the source. This '
            'could be the URL of the source file (if one exists) or of a webpage.'
        ),
    )
    location = models.ForeignKey(
        to='places.Place',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('location'),
    )
    publication_date = HistoricDateTimeField(
        verbose_name=_('publication date'), null=True, blank=True
    )
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
        verbose_name=_('URL'),
        max_length=MAX_URL_LENGTH,
        null=True,
        blank=True,
        help_text=(
            'URL where the source can be accessed online (outside ModularHistory)'
        ),
    )

    class Meta:
        ordering = ['-date']

    objects = PolymorphicSourceManager.from_queryset(PolymorphicSourceQuerySet)()
    searchable_fields = ['citation_string', 'description']
    serializer = SourceSerializer
    slug_base_field = 'title'

    def __html__(self) -> str:
        """
        Return the source's HTML representation, not including its containers.

        Must be defined by models inheriting from Source.
        """
        raise NotImplementedError

    def __str__(self):
        """Return the source's string representation."""
        return self.citation_string

    def clean(self):
        """Prepare the source to be saved."""
        super().clean()
        # Ensure a date value is set, if date is not explicitly made nullable.
        if not self.date and not self.date_nullable:
            raise ValidationError('Date is not nullable.')
        # Update the source's calculated fields.
        try:
            # Note: At this stage, changes to m2m relationships will not have
            # been processed. Calculated fields must be updated again after any
            # changes are made to the source's m2m relationships. This is handled
            # with "signals" (see apps/sources/signals.py).
            self.update_calculated_fields()
        except ValidationError:
            raise  # Re-raise any validation errors.
        except Exception as err:
            logging.error(f'{err}')
            raise ValidationError(f'Failed validation due to error: {err}')

    @property
    def ctype(self) -> ContentType:
        """Alias polymorphic_ctype."""
        return self.polymorphic_ctype

    @property
    def ctype_name(self) -> ContentType:
        """Return the model instance's ContentType."""
        return self.ctype.model

    @property
    def escaped_citation_html(self) -> SafeString:
        """Return the escaped citation HTML (for display in the Django admin)."""
        return format_html(self.citation_html)

    def get_attributee_html(self) -> str:
        """Return an HTML string representing the source's attributees."""
        # Avoid attempting to access a m2m relationship on a not-yet-saved source.
        m2m_relation_exists = (
            self.attributees.exists() if not self._state.adding else False
        )
        if m2m_relation_exists or self.attributee_string:
            if self.attributee_string:
                # Use attributee_string to generate attributee_html, if possible.
                attributee_html = self.attributee_string
                if m2m_relation_exists:
                    logging.debug('Generating attributee HTML from preset string...')
                    for entity in self.attributees.all().iterator():
                        if entity.name in attributee_html:
                            attributee_html = attributee_html.replace(
                                entity.name, entity.name_html
                            )
                return format_html(attributee_html)
            # Generate attributee_html from attributees (m2m relationship).
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
        return ''

    def get_citation_html(self) -> str:
        """Return the HTML representation of the source, including its containers."""
        html = self.__html__()
        containment_html = self.containment_html or self.get_containment_html()
        if containment_html:
            html = f'{html}, {containment_html}'
        elif getattr(self, 'page_number', None):
            page_number_html = self.get_page_number_html()
            html = f'{html}, {page_number_html}'
        if not self.file:
            if self.link and self.link not in html:
                html = f'{html}, retrieved from {self.link}'
        # TODO: Do something else with the information URL.
        # It shouldn't be part of the citation string, but we should use it.
        # if getattr(self, 'information_url', None) and self.information_url:
        #     html = (
        #         f'{html}, information available at '
        #         f'{compose_link(self.information_url, href=self.information_url, target="_blank")}'
        #     )
        return format_html(fix_comma_positions(html))

    def get_containment_html(self) -> str:
        """Return a list of strings representing the source's containers."""
        # Avoid accessing a m2m relationship on a not-yet-saved source.
        if self._state.adding:
            logging.debug('Containments of an unsaved source cannot be accessed.')
            return ''
        containments: QuerySet[
            'SourceContainment'
        ] = self.source_containments.select_related('container').order_by('position')
        container_strings: List[str] = []
        same_creator = True
        containment: SourceContainment
        for containment in containments[:2]:
            container: Source = containment.container
            container_html = f'{container.citation_html}'
            # Determine whether the container has the same attributee.
            if container.attributee_string != self.attributee_string:
                same_creator = False
            # Remove redundant creator string if necessary.
            creator_string_is_duplicated = (
                same_creator
                and self.attributee_html
                and self.attributee_html in container_html
            )
            if creator_string_is_duplicated:
                container_html = container_html[len(f'{self.attributee_html}, ') :]
            # Include the page number.
            if containment.page_number:
                page_number_html = container.get_page_number_html(
                    page_number=containment.page_number,
                    end_page_number=containment.end_page_number,
                )
                container_html = f'{container_html}, {page_number_html}'
            container_html = (
                f'{containment.phrase} in {container_html}'
                if containment.phrase
                else f'in {container_html}'
            )
            container_strings.append(container_html)
        return ', and '.join(container_strings)

    def get_date(self) -> Optional[HistoricDateTime]:
        """Get the source's date."""
        if self.date:
            return self.date
        elif not self._state.adding and self.containers.exists():
            try:
                containment: SourceContainment = (
                    self.source_containments.first().select_related('container')
                )
                return containment.container.date
            except Exception:
                pass
        return None

    # TODO: after deploying to prod and copying deprecated_href to the new href field,
    # remove the @property and @retrieve_or_compute decorators and rename this method
    # to get_href.
    @property  # type: ignore
    @retrieve_or_compute(attribute_name='href')
    def deprecated_href(self) -> str:
        """
        Return the href to use when providing a link to the source.

        If the source has a file, the URL of the file is returned;
        otherwise, the source's `url` field value is returned.
        """
        if self.file:
            url = self.file.url
            page_number = self.file.default_page_number
            if getattr(self, 'page_number', None):
                page_number = self.page_number + self.file.page_offset
            if page_number:
                url = _set_page_number(url, page_number)
        else:
            url = self.url or ''
            page_number = getattr(self, 'page_number', None)
            # TODO: refactor?
            if page_number:
                if 'www.sacred-texts.com' in url:
                    url = f'{url}#page_{page_number}'
                elif 'josephsmithpapers.org' in url:
                    url = f'{url}/{page_number}'
        return url

    def get_page_number_html(
        self, page_number: Optional[int] = None, end_page_number: Optional[int] = None
    ) -> str:
        page_number = page_number or self.page_number
        end_page_number = end_page_number or self.end_page_number
        if page_number:
            pn = self.get_page_number_link(page_number=page_number) or page_number
            if end_page_number:
                end_pn = (
                    self.get_page_number_link(page_number=end_page_number)
                    or end_page_number
                )
                return f'pp. {pn}–{end_pn}'
            return f'p. {pn}'
        return ''

    def get_page_number_link(self, page_number: Optional[int] = None) -> str:
        """Return a simple link to a specific page of the source file."""
        page_number = page_number or self.page_number
        url = self.get_page_number_url(page_number=page_number)
        if url:
            # Example: '<a href="https://..." class="display-source" target="_blank">25</a>'
            return compose_link(
                page_number, href=url, klass='display-source', target=NEW_TAB
            )
        return ''

    def get_page_number_url(self, page_number: Optional[int] = None) -> str:
        """Return the URL for a specific page of the source file."""
        if self.file:
            url = self.file.url
            page_number = page_number or self.page_number
            page_number += self.file.page_offset
            return _set_page_number(url, page_number)
        return ''

    @property
    def link(self) -> Optional[SafeString]:
        """Return an HTML link element containing the source URL, if one exists."""
        if self.url:
            return format_html(
                f'<a href="{self.url}" class="url" target="_blank">{self.url}</a>'
            )
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

    def update_calculated_fields(self):
        """
        Update the source's calculated fields (e.g., citation_html).

        Calculated fields may depend on many-to-many (m2m) relationships (as
        well as on the source's own attributes), so this method should be called
        not only during source cleaning/saving but also after m2m relationships
        are added or removed (via "signals"; see apps/sources/signals.py).

        However, since this method may be called on a new source before it is
        initially saved to the database (i.e., before it gains a primary key),
        and since attempting to access m2m relationships on a model instance that
        has not yet been saved to the db would normally result in an error, any
        logic contained in this method must take this into account and tolerate
        an inability to access the source's m2m relationships.
        """
        # Calculate the attributee HTML and string.
        self.attributee_html = self.get_attributee_html()
        # Compute attributee_string from attributee_html only if
        # attributee_string was not already manually set.
        if not self.attributee_string:
            self.attributee_string = soupify(self.attributee_html).get_text()

        # If needed (and possible), use the container's source file.
        if not self.file and not self._state.adding:
            try:
                containment: SourceContainment = (
                    self.source_containments.first().select_related('container')
                )
                self.file = containment.container.file
            except Exception as err:
                logging.debug(f'Could not set source file from container: {err}')

        # Calculate the containment HTML.
        self.containment_html = self.get_containment_html()

        # Calculate the citation HTML.
        self.citation_html = self.get_citation_html()

        # Set citation_string to the text version of citation_html.
        if self.containment_html and self.containment_html in self.citation_html:
            # Omit the containment string and anything following it.
            index = self.citation_html.index(self.containment_html)
            self.citation_string = soupify(
                self.citation_html[:index].rstrip(', ')
            ).get_text()
        else:
            self.citation_string = soupify(self.citation_html).get_text()

    @staticmethod
    def components_to_html(components: Sequence[Optional[str]]):
        """Combine a list of HTML components into an HTML string."""
        return components_to_html(components, delimiter=COMPONENT_DELIMITER)


def _set_page_number(url: str, page_number: Union[str, int]) -> str:
    page_param = 'page'
    if f'{page_param}=' in url:
        url = re.sub(rf'{page_param}=\d+', f'{page_param}={page_number}', url)
    else:
        url = f'{url}#{page_param}={page_number}'
    return url
