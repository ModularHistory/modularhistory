import re
from typing import List, Optional, TYPE_CHECKING

from bs4 import BeautifulSoup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE, SET_NULL
from django.utils.safestring import SafeText, mark_safe
from gm2m import GM2MField as GenericManyToManyField

from history.fields import HTMLField, HistoricDateTimeField
from history.models import Model, DatedModel, SearchableMixin, PolymorphicModel
from history.structures.historic_datetime import HistoricDateTime
from .source_file import SourceFile
from ..manager import Manager

if TYPE_CHECKING:
    from entities.models import Entity


class Source(PolymorphicModel, DatedModel, SearchableMixin):
    """A source for quotes or historical information."""
    db_string = models.CharField(verbose_name='database string', max_length=500, blank=True, unique=True)
    attributees = ManyToManyField(
        'entities.Entity', related_name='attributed_sources',
        through='SourceAttribution',
        blank=True  # Some sources may not have attributees.
    )
    url = models.URLField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    date = HistoricDateTimeField(null=True, blank=True)
    publication_date = HistoricDateTimeField(null=True, blank=True)
    location = ForeignKey(
        'places.Place', related_name='publications',
        null=True, blank=True,
        on_delete=SET_NULL
    )
    db_file = ForeignKey(
        SourceFile, related_name='sources',
        null=True, blank=True,
        on_delete=SET_NULL, verbose_name='file'
    )
    creators = models.CharField(max_length=100, null=True, blank=True)
    containers = ManyToManyField(
        'self', related_name='contained_sources',
        through='SourceContainment',
        through_fields=('source', 'container'),
        symmetrical=False,
        blank=True
    )
    related = GenericManyToManyField(
        'quotes.Quote', 'occurrences.Occurrence',
        through='sources.Citation',
        related_name='sources',
        blank=True
    )

    HISTORICAL_ITEM_TYPE = 'publication'

    objects: Manager = Manager()
    searchable_fields = ['db_string', 'description']

    class Meta:
        ordering = ['creators', '-date']

    def __str__(self):
        return str(self.object)

    @property
    def admin_file_link(self) -> SafeText:
        element = ''
        if self.file:
            element = (f'<a class="btn btn-small btn-default display-source"'
                       f' href="{self.object.file_url}" target="_blank">'
                       f'<i class="fa fa-search"></i></a>')
        return mark_safe(element)

    @property
    def attributee_string(self) -> Optional[str]:
        if self.creators:
            return self.creators
        # Check for pk to avoid RecursionErrors with not-yet-saved objects
        elif not self.pk or not self.attributees.exists():
            return None
        attributees = self.ordered_attributees
        n_attributions = len(attributees)
        first_attributee = attributees[0]
        string = str(first_attributee)
        if n_attributions == 2:
            string += f' and {attributees[1]}'
        elif n_attributions == 3:
            string += f', {attributees[1]}, and {attributees[2]}'
        elif n_attributions > 3:
            string += f' et al.'
        return mark_safe(string)

    @property
    def container(self) -> Optional['Source']:
        if not self.containment:
            return None
        return self.containment.container

    @property
    def containment(self) -> Optional['SourceContainment']:
        if not self.source_containments.exists():
            return None
        return self.source_containments.order_by('position')[0]

    @property
    def file(self) -> Optional[SourceFile]:
        return self.db_file or (self.container.db_file if self.container else None)

    @file.setter
    def file(self, value):
        self.db_file = value

    @property
    def file_url(self) -> Optional[str]:
        file = self.file
        return file.url if file else None

    @property
    def _html(self) -> SafeText:
        """Must be defined by inheriting models."""
        return self.object._html

    def html(self) -> SafeText:
        # TODO: html methods should be split into different classes and/or mixins.
        html = self._html
        if self.source_containments.exists():
            containments = self.source_containments.order_by('position')[:2]
            container_strings = []
            same_creator = True
            for c in containments:
                if c.container.attributee_string != self.attributee_string:
                    same_creator = False
                container_html = c.container.html

                # Remove redundant creator string
                if (same_creator and self.attributee_string and
                        self.attributee_string in container_html):
                    container_html = container_html[len(f'{self.attributee_string}, '):]

                # Include the page number
                if c.page_number:
                    _url = self.file_url or None

                    def get_page_number_url(page_number, url=_url) -> Optional[str]:
                        if not url:
                            return None
                        page_number += c.container.file.page_offset
                        print(f'>>>>> setting {c.container} pn: {page_number}')
                        if 'page=' in url:
                            original = re.match(r'page=(\d+)').group(1)
                            print(f">>>>> originally {original}")
                            url = re.sub(r'page=\d+', f'page={page_number}', url)
                        else:
                            url += f'#page={page_number}'
                        return url

                    def get_page_number_link(url, page_number) -> Optional[str]:
                        if not url:
                            return None
                        return (f'<a href="{url}" target="_blank" '
                                f'class="display-source">{page_number}</a>')

                    pn = c.page_number
                    pn_url = get_page_number_url(pn)
                    pn = get_page_number_link(pn_url, pn) or pn
                    if c.end_page_number:
                        end_pn = c.end_page_number
                        end_pn_url = get_page_number_url(end_pn)
                        end_pn = get_page_number_link(end_pn_url, end_pn) or end_pn
                        container_html += f', pp. {pn}–{end_pn}'
                    else:
                        container_html += f', p. {pn}'

                container_html = (f'{c.phrase} in {container_html}' if c.phrase
                                  else f'in {container_html}')
                container_strings.append(container_html)
            containers = ', and '.join(container_strings)
            html += f', {containers}'
        if not self.file:
            if self.url and self.link not in html:
                html += f', retrieved from {self.link}'
        if getattr(self.object, 'information_url', None) and self.information_url:
            html += (
                f', information available at <a target="_blank" href="{self.information_url}">'
                f'{self.information_url}</a>'
            )
        # Fix placement of commas after double-quoted titles
        html = html.replace('," ,', ',"')
        html = html.replace('",', ',"')
        return mark_safe(html)
        # TODO: Remove search icon; insert link intelligently
        # if self.file_url:
        #     html += (
        #         f'<a href="{self.file_url}" class="mx-1 display-source"'
        #         f' data-toggle="modal" data-target="#modal">'
        #         f'<i class="fas fa-search"></i>'
        #         f'</a>'
        #     )
        # elif self.url:
        #     link = self.url
        #     if self.page_number and 'www.sacred-texts.com' in link:
        #         link += f'#page_{self.page_number}'
        #     html += (
        #         f'<a href="{link}" class="mx-1" target="_blank">'
        #         f'<i class="fas fa-search"></i>'
        #         f'</a>'
        #     )
    html.admin_order_field = 'db_string'
    html = property(html)

    @property
    def link(self) -> Optional[SafeText]:
        return f'<a target="_blank" href="{self.url}">{self.url}</a>' if self.url else None

    @property
    def object(self) -> 'Source':
        """Return the object with the correct content type."""
        polymorphic_ctype_id = getattr(self, 'polymorphic_ctype_id', None)
        if polymorphic_ctype_id:
            try:
                ct = ContentType.objects.get(id=polymorphic_ctype_id)
                return ct.model_class().objects.get(id=self.id)
            except Exception as e:
                print(f'EXCEPTION: Trying to get child object for {self} resulted in: {e}')
        return self

    @property
    def ordered_attributees(self) -> Optional[List['Entity']]:
        if not self.pk or not self.attributees.exists():
            return None
        return [attribution.attributee for attribution in self.attributions.all()]

    @property
    def string(self) -> str:
        # TODO: String methods should be split into different classes and/or mixins.
        if hasattr(self.object, 'string_override'):
            return mark_safe(self.object.string_override)
        return BeautifulSoup(self.html, features='lxml').get_text()

    def clean(self):
        super().clean()
        if Source.objects.exclude(pk=self.pk).filter(db_string=self.db_string).exists():
            raise ValidationError(
                f'Unable to save this source because it duplicates an existing source '
                f'or has an identical string: {self.db_string}'
            )
        if self.id or self.pk:  # If this source is not being newly created
            for container in self.containers.all():
                if self in container.containers.all():
                    raise ValidationError(
                        f'This source cannot be contained by {container}, '
                        f'because that source is already contained by this source.'
                    )

    def get_date(self) -> Optional[HistoricDateTime]:
        if self.date:
            return self.date
        elif self.container and self.container.date:
            return self.container.date
        return None

        # # Create related historical occurrence
        # if not Episode.objects.filter(type=self.HISTORICAL_ITEM_TYPE).exists():
        #     Episode.objects.create(
        #         type=self.HISTORICAL_ITEM_TYPE,
        #     )

    def save(self, *args, **kwargs):
        self.clean()
        self.db_string = self.string
        super().save(*args, **kwargs)


class TitleMixin(Model):
    title = models.CharField(max_length=250, null=True, blank=True)

    url: Optional[str]
    file: Optional[SourceFile]
    file_url: Optional[str]

    class Meta:
        abstract = True

    @property
    def title_html(self) -> SafeText:
        html = self.title
        url = self.url
        if self.file_url:
            url = self.file_url
            page_number = self.file.default_page_number
            if page_number:
                if 'page=' in url:
                    url = re.sub(r'page=\d+', f'page={page_number}', url)
                else:
                    url += f'#page={page_number}'
        if url:
            html = (f'<a href="{url}" target="_blank" '
                    f'class="source-title display-source">{html}</a>')
        return mark_safe(html)


containment_phrases = (
    ('', '-----'),
    ('archived', 'archived'),
    ('cited', 'cited'),
    ('copy', 'copy'),
    ('quoted', 'quoted'),
    ('recorded', 'recorded'),
    ('reproduced', 'reproduced'),
    ('transcribed', 'transcribed')
)


class SourceContainment(Model):
    source = ForeignKey(Source, on_delete=CASCADE, related_name='source_containments')
    container = ForeignKey(Source, on_delete=CASCADE, related_name='container_containments')
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=1)
    phrase = models.CharField(max_length=12, choices=containment_phrases, default='', blank=True)

    class Meta:
        ordering = ['position', 'source']

    def __str__(self):
        return mark_safe(f'{self.phrase} in {self.container}')


class TextualSource(Source):
    editors = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def file_page_number(self) -> Optional[int]:
        file = self.file
        if file:
            if self.containment and self.containment.page_number:
                return self.containment.page_number + file.page_offset
            return file.first_page_number + file.page_offset
        return None

    @property
    def file_url(self) -> Optional[str]:
        file_url = super().file_url
        if file_url and self.file_page_number:
            file_url += f'#page={self.file_page_number}'
        return file_url


class SourceAttribution(Model):
    """An entity (e.g., a writer or organization) to which a source is attributed."""
    source = ForeignKey(Source, on_delete=CASCADE,
                        related_name='attributions')
    attributee = ForeignKey('entities.Entity', on_delete=CASCADE,
                            related_name='source_attributions')
    position = models.PositiveSmallIntegerField(default=1, blank=True)

    def __str__(self):
        return self.attributee.verbose_name or f'{self.attributee}'


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
