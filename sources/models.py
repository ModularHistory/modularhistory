from typing import Optional, Tuple
import re
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE, PROTECT, SET_NULL
from django.utils.safestring import SafeText, mark_safe
from taggit.models import TaggedItemBase
from datetime import date
from entities.models import Entity
from history.fields import HTMLField, HistoricDateField
from history.models import Model, PolymorphicModel
from django.core.exceptions import ValidationError


class SourceTag(TaggedItemBase):
    """A source tag"""
    content_object = ForeignKey('Source', on_delete=CASCADE)


# class SourceFile(Model):
#     file = models.FileField(upload_to='sources/', null=True, blank=True)
#     page_offset = models.PositiveSmallIntegerField(null=True, blank=True, default=0)


class Source(PolymorphicModel):
    """A source for quotes or historical information."""
    title = models.CharField(max_length=100, null=True, blank=True)
    creators = models.CharField(max_length=100, null=True, blank=True)
    editors = models.CharField(max_length=100, null=True, blank=True)
    attributees = ManyToManyField(Entity, through='SourceAttribution')
    link = models.CharField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    date = HistoricDateField(null=True, blank=True)
    publication_date = HistoricDateField(null=True, blank=True)
    year = ForeignKey('occurrences.Year', related_name='publications', on_delete=PROTECT, null=True, blank=True)
    container = ForeignKey('self', related_name='sources_contained', on_delete=CASCADE, null=True, blank=True)
    location = ForeignKey('places.Place', related_name='publications', on_delete=PROTECT, null=True, blank=True)
    citations = ManyToManyField('self', related_name='sources', blank=True)
    file = models.FileField(upload_to='sources/', null=True, blank=True)

    HISTORICAL_ITEM_TYPE = 'publication'

    class Meta:
        unique_together = [['title', 'date']]
        ordering = ['creators', '-year', '-date']

    @property
    def file_url(self) -> Optional[str]:
        file_url = None
        if self.file:
            file_url = self.file.url
        elif self.container and self.container.file:
            file_url = self.container.file.url
        return file_url

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
            self.date = date(self.year.common_era, month=1, day=1)

        # # Create related historical occurrence
        # if not Episode.objects.filter(type=self.HISTORICAL_ITEM_TYPE).exists():
        #     Episode.objects.create(
        #         type=self.HISTORICAL_ITEM_TYPE,
        #     )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TextualSource(Source):
    file_page_offset = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        abstract = True

    @property
    def file_page_number(self) -> Optional[int]:
        if self.file:
            return self.file_page_offset or 1
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
        string = f'{self.creators}, ' or ''
        string += f'<i>{self.title}</i>'
        string += f', {self.date.year}' if self.date else ''
        return mark_safe(string)


class Piece(TextualSource):
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def file_page_number(self) -> Optional[int]:
        page_number = None
        if self.page_number:
            page_number = self.page_number + (self.file_page_offset or 0)
        return page_number


class Essay(Piece):
    def __str__(self):
        string = f'{self.creators}, ' or ''
        string += f'''"{self.title}{'," ' if self.date or self.container else '"'}'''
        string += (f'{self.date.year}' if self.date else '')  # + (', ' if self.container else '')
        if self.container:
            container_string = str(self.container)
            if self.container.creators == self.creators:
                container_string = container_string[len(f'{self.creators}, '):]
            string += f' (in {container_string})'
        return mark_safe(string)


class Publisher(Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    aliases = models.CharField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class Journal(Publisher):
    pass


class Newspaper(Publisher):
    pass


class Magazine(Publisher):
    pass


class Article(Piece):
    publication_name = models.CharField(max_length=100, null=True, blank=True)
    number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class JournalArticle(Article):
    journal = ForeignKey(Journal, related_name='journal_articles', null=True, blank=True, on_delete=CASCADE)
    volume_number = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self) -> SafeText:
        journal_str = str(self.journal or self.publication_name)
        journal_str += f', vol. {self.volume_number}' if self.volume_number else ''
        journal_str += f', no. {self.number}' if self.number else ''
        string = f'{self.creators}, "{self.title}," <i>{journal_str}</i>'
        string += f', {self.date.year}' if self.date else ''
        return mark_safe(string)


class NewspaperArticle(Article):
    newspaper = ForeignKey(Newspaper, related_name='newspaper_articles', null=True, blank=True, on_delete=CASCADE)

    def __str__(self) -> SafeText:
        string = ''
        string += f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'<i>{self.newspaper or self.publication_name}</i>, {self.date.strftime("%d %b %Y")}'
        return mark_safe(string)


class MagazineArticle(Article):
    magazine = ForeignKey(Magazine, related_name='magazine_articles', null=True, blank=True, on_delete=CASCADE)
    volume_number = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self) -> SafeText:
        string = ''
        string += f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'<i>{self.magazine or self.publication_name}</i>, '
        string += f'vol. {self.volume_number}, ' if self.volume_number else ''
        string += f'no. {self.number}, ' if self.number else ''
        string += f'{self.date.strftime("%d %b %Y") if self.date else self.year.common_era}'
        return mark_safe(string)


# class Repository(Model):
#     pass


class BaseDocument(TextualSource):
    repository_name = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='the name of the collecting institution'
    )
    # repository = ForeignKey(Repository, related_name='documents', on_delete=CASCADE)
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


class Document(BaseDocument):
    def __str__(self) -> SafeText:
        string = ''
        string += f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'{self.date}, ' if self.date else f'{self.year.get_pretty_string()}, ' if self.year else ''
        string += f'in ' if self.repository_name or self.location_info else ''
        string += ', '.join([item for item in (self.repository_name, self.location_info) if item])
        return mark_safe(string)


class Letter(BaseDocument):
    recipient = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> SafeText:
        string = f'Letter from {self.creators} to {self.recipient or "<Unknown>"}, '
        string += (f'{self.date.year}' if self.date else '')  # + (', ' if self.container else '')
        if self.container:
            container_string = str(self.container)
            if self.container.creators == self.creators:
                container_string = container_string[len(f'{self.creators}, '):]
            string += f' (in {container_string})'
        return mark_safe(string)


class SpokenSource(Source):
    venue = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


speech_types = (
    ('speech', 'speech'),
    ('address', 'address'),
    ('statement', 'statement'),
)


class Speech(SpokenSource):
    type = models.CharField(max_length=10, choices=speech_types, default='speech')
    audience = models.CharField(max_length=100, null=True, blank=True)

    HISTORICAL_ITEM_TYPE = 'delivery'

    def __str__(self):
        string = f'{self.creators}, "{self.title}," {self.type}'
        string += ' delivered' if self.type and self.type == 'speech' else ''
        string += f' to {self.audience}' if self.audience else ''
        string += f' at {self.venue}' if self.venue else ''
        string += f', {self.date}'
        return string


class Lecture(SpokenSource):
    HISTORICAL_ITEM_TYPE = 'delivery'

    def __str__(self):
        return f'{self.creators}, "{self.title}," lecture delivered at {self.venue}, {self.date}'


class Interview(SpokenSource):
    HISTORICAL_ITEM_TYPE = 'interview'

    interviewers = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return mark_safe(f'{self.creators} to {self.interviewers or "interviewer"}, {self.container}')


class VideoSource(Source):
    class Meta:
        abstract = True


class Documentary(VideoSource):
    def __str__(self) -> SafeText:
        string = f'{self.creators}, '
        string += f'<em>{self.title}</em>," ' if self.title else ''
        string += f'{self.date}, ' if self.date else f'{self.year.get_pretty_string()}, ' if self.year else ''
        return mark_safe(string)


class SourceAttribution(Model):
    """An entity (e.g., a writer or organization) to which a source is attributed."""
    source = ForeignKey(Source, on_delete=PROTECT)
    attributee = ForeignKey(Entity, on_delete=PROTECT, related_name='source_attributions')
    position = models.PositiveSmallIntegerField(default=1, blank=True)


source_types = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
    ('T', 'Tertiary')
)


class SourceReference(Model):
    """Abstract base class for a reference to a source."""
    source: Source
    source_type = models.CharField(max_length=3, choices=source_types, null=True, blank=True)
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
        return mark_safe(f'{self.source}{", " if page_string else ""}{page_string}')

    @property
    def source_file_page_number(self) -> Optional[int]:
        if self.page_number and self.source.file_page_offset:
            return self.page_number + self.source.file_page_offset
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
