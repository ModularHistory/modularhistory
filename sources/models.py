import re
from typing import Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE, PROTECT, SET_NULL
from django.utils.safestring import SafeText, mark_safe
from taggit.models import TaggedItemBase

from history.fields import (
    HTMLField,
    HistoricDateField,
    HistoricDateTimeField,
    SourceFileField, upload_to
)
from history.models import Model, PolymorphicModel
from history.structures.source_file import SourceFile
from history.structures.historic_datetime import HistoricDateTime
from places.models import Venue


class SourceTag(TaggedItemBase):
    """A source tag"""
    content_object = ForeignKey('Source', on_delete=CASCADE)


# class SourceFile(Model):
#     file = models.FileField(upload_to='sources/', null=True, blank=True)


class Source(PolymorphicModel):
    """A source for quotes or historical information."""
    attributees = ManyToManyField('entities.Entity', through='SourceAttribution')
    title = models.CharField(max_length=250, null=True, blank=True)
    creators = models.CharField(max_length=100, null=True, blank=True)
    editors = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    date = HistoricDateTimeField(null=True, blank=True)
    publication_date = HistoricDateField(null=True, blank=True)
    year = ForeignKey('occurrences.Year', related_name='publications', on_delete=PROTECT, null=True, blank=True)
    containers = ManyToManyField('self', through='SourceContainment', symmetrical=False,
                                 through_fields=('source', 'container'), related_name='contained_sources', blank=True)
    location = ForeignKey('places.Place', related_name='publications', on_delete=PROTECT, null=True, blank=True)
    file = SourceFileField(upload_to=upload_to('sources/'), null=True, blank=True)
    citations = ManyToManyField('self', related_name='sources', blank=True)
    db_string = models.CharField(max_length=500, null=True, blank=True)

    HISTORICAL_ITEM_TYPE = 'publication'

    searchable_fields = ['db_string', 'description']

    class Meta:
        unique_together = [['title', 'date']]
        ordering = ['creators', '-year', '-date']

    def __str__(self):
        return str(self.object)

    @property
    def admin_file_link(self) -> SafeText:
        element = ''
        if self.get_file():
            element = f'<a class="btn display-source" href="{self.object.file_url}" target="_blank">file</a>'
        return mark_safe(element)

    @property
    def container(self) -> Optional['Source']:
        if not self.source_containments.exists():
            return None
        return self.source_containments.order_by('position')[0].container

    @property
    def date_string(self) -> str:
        return self.date.string if self.date else ''

    @property
    def object(self) -> 'Source':
        """Return the object with the correct content type."""
        ct = ContentType.objects.get(id=self.polymorphic_ctype_id)
        return ct.model_class().objects.get(id=self.id)

    @property
    def string(self) -> SafeText:
        string = str(self)
        if self.source_containments.exists():
            containments = self.source_containments.order_by('position')[:2]
            containers = [containment.container for containment in containments]
            container_strings = []
            same_creator = True
            for c in containers:
                if c.creators != self.creators:
                    same_creator = False
                container_string = str(c)
                if same_creator:
                    container_string = container_string[len(f'{self.creators}, '):]
                container_strings.append(container_string)
            containers = ', and '.join(container_strings)
            string += f', in {containers}'
        return mark_safe(string)

    @property
    def file_url(self) -> Optional[str]:
        file = self.get_file()
        return file.url if file else None

    def get_file(self) -> Optional[SourceFile]:
        return (self.file if self.file
                else self.container.file if self.container and self.container.file
                else None)

    def natural_key(self) -> Tuple:
        return self.title, self.date

    def clean(self):
        from occurrences.models import Year, Episode

        # Set year and date
        if self.date:
            year, _ = Year.objects.get_or_create(common_era=self.date.year)
            self.year = year
        elif self.year:
            # TODO
            self.date = HistoricDateTime(self.year.common_era, month=1, day=1, hour=1, minute=1, second=1)

        # # Create related historical occurrence
        # if not Episode.objects.filter(type=self.HISTORICAL_ITEM_TYPE).exists():
        #     Episode.objects.create(
        #         type=self.HISTORICAL_ITEM_TYPE,
        #     )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.db_string = self.string
        super().save(*args, **kwargs)


class SourceContainment(Model):
    source = ForeignKey(Source, on_delete=CASCADE, related_name='source_containments')
    container = ForeignKey(Source, on_delete=CASCADE, related_name='container_containments')
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=1)


class TextualSource(Source):
    class Meta:
        abstract = True

    @property
    def file_page_number(self) -> Optional[int]:
        file = self.get_file()
        if file:
            return file.page_offset or 1
        return None

    @property
    def file_url(self) -> Optional[str]:
        file_url = super().file_url
        if file_url and self.file_page_number:
            file_url += f'#page={self.file_page_number}'
        return file_url


class Book(TextualSource):
    publisher = models.CharField(max_length=100, null=True, blank=True)
    edition_number = models.PositiveSmallIntegerField(default=1)
    volume_number = models.PositiveSmallIntegerField(null=True, blank=True)
    original_book = ForeignKey('self', related_name='subsequent_editions', blank=True, null=True, on_delete=SET_NULL)
    original_publication_date = HistoricDateField(null=True, blank=True)

    def __str__(self):
        # string = f'{self.creators}, ' or ''
        # string += self.title
        # string += self.date.year if self.date else ''
        string = f'{self.creators}, ' if self.creators else ''
        string += f'<i>{self.title}</i>'
        string += f', ed. {self.editors}' if self.editors else ''
        if (self.edition_number and self.edition_number > 1) or self.original_book:
            string += f', {self.year.common_era} edition'
        else:
            string += f', {self.date.year}' if self.date else ''
        return mark_safe(string)


class Piece(TextualSource):
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def string(self) -> SafeText:
        string = super().string
        # Fix placement of commas after double-quoted titles
        string = string.replace('," ,', ',"')
        string = string.replace('",', ',"')
        return mark_safe(string)

    @property
    def file_page_number(self) -> Optional[int]:
        file = self.get_file()
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
        return None


class Essay(Piece):
    def __str__(self) -> SafeText:
        string = f'{self.creators}, ' or ''
        string += f'"{self.title}"'
        # NOTE: punctuation (quotation marks and commas) are rearranged in the string
        string += f', {self.date.string}' if self.date else ''  # + (', ' if self.container else '')
        string = string.replace('",', ',"')
        return mark_safe(string)


publication_types = (
    ('journal', 'Journal'),
    ('newspaper', 'Newspaper'),
    ('magazine', 'Magazine'),
)


class Publication(Model):
    type = models.CharField(max_length=10, null=True, blank=True, choices=publication_types)
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    aliases = models.CharField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    searchable_fields = ['name', 'aliases']

    def __str__(self) -> SafeText:
        return mark_safe(f'<i>{self.name}</i>')


class PublicationVolume(Model):
    publication = ForeignKey(Publication, null=True, blank=True, on_delete=CASCADE)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    date = HistoricDateTimeField(null=True, blank=True)
    file = SourceFileField(upload_to='sources/', null=True, blank=True)

    class Meta:
        ordering = ['publication', 'number']

    def __str__(self) -> SafeText:
        string = f'{self.publication}, vol. {self.number}'
        # string += f', {self.date.string}' if self.date else ''
        return mark_safe(string)


class PublicationNumber(Model):
    publication = ForeignKey(Publication, on_delete=CASCADE)
    volume = ForeignKey(PublicationVolume, null=True, blank=True, on_delete=CASCADE)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    date = HistoricDateTimeField(null=True, blank=True)
    file = SourceFileField(upload_to='sources/', null=True, blank=True)

    class Meta:
        ordering = ['volume', 'number']

    def __str__(self) -> SafeText:
        string = f'{self.publication}, '
        string += f'vol. {self.volume.number}, ' if self.volume else ''
        string += f'no. {self.number}'
        # string += f', {self.date.string}' if self.date else ''
        return mark_safe(string)

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude=exclude, validate_unique=validate_unique)
        if self.volume and self.publication and self.volume.publication != self.publication:
            raise ValidationError('Publication and volume are inconsistent.')
        if self.volume and not self.publication:
            self.publication = self.volume.publication


class Article(Piece):
    number = ForeignKey(PublicationNumber, null=True, blank=True, on_delete=CASCADE)
    volume = ForeignKey(PublicationVolume, null=True, blank=True, on_delete=CASCADE)
    publication = ForeignKey(Publication, null=True, blank=True, on_delete=CASCADE)

    searchable_fields = ['db_string', 'publication__name']

    def __str__(self) -> SafeText:
        string = f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'{self.number or self.volume or self.publication}'
        string += f', {self.date.string}' if self.date else ''
        return mark_safe(string)

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude=exclude, validate_unique=validate_unique)
        if self.number:
            if self.number.date and not self.date:
                self.date = self.number.date
            if self.volume and self.number.volume != self.volume:
                raise ValidationError('Number and volume are inconsistent.')
            if not self.volume:
                self.volume = self.number.volume
        if self.volume and not self.publication:
            self.publication = self.volume.publication

    def get_file(self) -> Optional[SourceFile]:
        return (self.file if self.file
                else self.number.file if self.number and self.number.file
                else self.volume.file if self.volume and self.volume.file
                else None)


class BaseDocument(TextualSource):
    collection = ForeignKey('Collection', related_name='%(class)s', null=True, blank=True, on_delete=CASCADE)
    repository_name = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='the name of the collecting institution'
    )
    collection_number = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='aka acquisition number'
    )
    location_info = models.CharField(
        max_length=400, null=True, blank=True,
        help_text='Ex: John H. Alexander Papers, Series 1: Correspondence, 1831-1848, Folder 1'
    )

    HISTORICAL_ITEM_TYPE = 'writing'

    class Meta:
        abstract = True


class Collection(Model):
    name = models.CharField(max_length=100, help_text='e.g., "Adam S. Bennion papers"')
    repository = ForeignKey('Repository', on_delete=CASCADE)

    def __str__(self):
        string = self.name
        string += f', {self.repository}' if self.repository else ''
        return string


class Repository(Model):
    name = models.CharField(max_length=100, null=True, blank=True,
                            help_text='e.g., "L. Tom Perry Special Collections"')
    location = models.CharField(max_length=100, null=True, blank=True,
                                help_text='e.g., "Harold B. Lee Library, Brigham Young University"')

    class Meta:
        verbose_name_plural = 'Repositories'

    def __str__(self):
        return f'{self.name}, {self.location}'


class Document(BaseDocument):
    def __str__(self) -> SafeText:
        string = ''
        string += f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'{self.date.string}, ' if self.date else f'{self.year.get_pretty_string()}, ' if self.year else ''
        string += f'in {self.collection}' if self.collection else ''
        return mark_safe(string)


class Letter(BaseDocument):
    recipient = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> SafeText:
        string = f'{self.creators}, letter to {self.recipient or "<Unknown>"}'
        if self.date:
            string += ', dated ' if self.date.day_is_known else ', '
            string += self.date.string
        string += f', in {self.collection}' if self.collection else ''
        return mark_safe(string)


class SpokenSource(Source):
    venue = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


speech_types = (
    ('speech', 'speech'),
    ('address', 'address'),
    ('discourse', 'discourse'),
    ('statement', 'statement'),
)


class Speech(SpokenSource):
    type = models.CharField(max_length=10, choices=speech_types, default='speech')
    audience = models.CharField(max_length=100, null=True, blank=True)

    HISTORICAL_ITEM_TYPE = 'delivery'

    class Meta:
        verbose_name_plural = 'Speeches'

    def __str__(self):
        string = f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'{self.type}' + (' delivered' if self.type in ('speech', 'discourse') else '')
        if self.audience or self.location:
            string += f' to {self.audience}' if self.audience else ''
            if self.location or self.venue:
                location = self.venue or self.location
                preposition = location.preposition if isinstance(location, Venue) else 'in'
                string += f' {preposition} {location}'
            string += ', '
        else:
            string += ' '
        string += self.date.string
        return string


class Lecture(SpokenSource):
    HISTORICAL_ITEM_TYPE = 'delivery'

    def __str__(self):
        string = f'{self.creators}, "{self.title}," lecture delivered at {self.venue}'
        string += f', {self.date.string}' if self.date else ''
        return string


class Interview(SpokenSource):
    HISTORICAL_ITEM_TYPE = 'interview'

    interviewers = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        string = f'{self.creators} to {self.interviewers or "interviewer"}, '
        string += f'{self.date.string}' if self.date else ''
        return mark_safe(string)


class VideoSource(Source):
    class Meta:
        abstract = True


class Documentary(VideoSource):
    def __str__(self) -> SafeText:
        string = f'{self.creators}, '
        string += f'<em>{self.title}</em>," ' if self.title else ''
        string += f'{self.date.string}, ' if self.date else f'{self.year.get_pretty_string()}, ' if self.year else ''
        return mark_safe(string)

    class Meta:
        verbose_name_plural = 'Documentaries'


class SourceAttribution(Model):
    """An entity (e.g., a writer or organization) to which a source is attributed."""
    source = ForeignKey(Source, on_delete=CASCADE)
    attributee = ForeignKey('entities.Entity', on_delete=CASCADE, related_name='source_attributions')
    position = models.PositiveSmallIntegerField(default=1, blank=True)


source_types = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
    ('T', 'Tertiary')
)


class SourceReference(Model):
    """Abstract base class for a reference to a source."""
    source: Source
    position = models.PositiveSmallIntegerField(verbose_name='reference position', default=1, blank=True)
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> SafeText:
        page_string = ''
        if self.page_number:
            page_string = f'p{"p" if self.end_page_number else ""}. {self.page_number}'
            if self.end_page_number:
                page_string += f'–{self.end_page_number}'
        return mark_safe(f'{self.source.string}{", " if page_string else ""}{page_string}')

    @property
    def source_file_page_number(self) -> Optional[int]:
        file = self.source.get_file()
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
            elif hasattr(self.source, 'file_page_number'):
                return self.source.file_page_number
        return None

    @property
    def source_file_url(self) -> Optional[str]:
        file_url = self.source.file_url
        if file_url:
            if 'page=' in file_url:
                file_url = re.sub(r'page=\d+', f'page={self.source_file_page_number}', file_url)
            else:
                file_url = file_url + f'#page={self.source_file_page_number}'
        return file_url

    def clean(self):
        if self.end_page_number and self.end_page_number < self.page_number:
            raise ValidationError('The end page number must be greater than the start page number.')


class SourceFactDerivation(SourceReference):
    source = ForeignKey(Source, related_name='fact_derivations', on_delete=CASCADE)
    fact = ForeignKey('topics.Fact', related_name='fact_derivations', on_delete=CASCADE)
