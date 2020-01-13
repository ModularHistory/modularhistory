from datetime import datetime
from decimal import Decimal, getcontext
from typing import Optional, Tuple

from django.db import models
from django.db.models import PROTECT, CASCADE, ManyToManyField, QuerySet
from django.template.defaultfilters import truncatechars
from django.utils.safestring import SafeText, mark_safe
from taggit.models import TaggedItemBase

from history.fields import HTMLField
from history.fields import HistoricDateField
from history.models import Model, PolymorphicModel, TaggableModel
from images.models import Image
from sources.models import Source, SourceReference


class Year(Model):
    """A year in history"""
    common_era_threshold = 1000000

    nickname = models.CharField(max_length=20, null=True, blank=True)
    common_era = models.DecimalField(max_digits=12, decimal_places=0, unique=True, blank=True, null=True)
    years_before_present = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    string = models.CharField(max_length=20, null=True, blank=True)

    searchable_fields = ['common_era', 'nickname']

    class Meta:
        ordering = ['-years_before_present']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_ce = self.common_era
        self.__initial_ybp = self.years_before_present

    def __str__(self):
        return self.string or self.get_pretty_string()

    def get_pretty_string(self) -> str:
        return (f'{self.years_before_present} YBP' if any([self.years_before_present and not self.common_era,
                                                           self.years_before_present > self.common_era_threshold])
                else f'{-self.common_era} BCE' if self.common_era < 0
                else f'{self.common_era} CE' if self.common_era >= 0
                else self)

    def natural_key(self) -> Tuple:
        return self.common_era,

    def clean(self):
        current_year = datetime.now().year
        getcontext().prec = 7
        if self.years_before_present:
            self.years_before_present = Decimal(f'{self.years_before_present}')
        if self.common_era and ((self.common_era != self.__initial_ce) or not self.years_before_present):
            self.years_before_present = Decimal(current_year - self.common_era)
        elif self.years_before_present and ((self.years_before_present != self.__initial_ybp) or not self.common_era):
            self.common_era = Decimal(f'''{-((self.years_before_present - current_year)
                                             if self.years_before_present <= self.common_era_threshold
                                             else self.years_before_present)}''')
        self.string = self.get_pretty_string()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OccurrenceImage(Model):
    occurrence = models.ForeignKey('Occurrence', on_delete=PROTECT)
    image = models.ForeignKey(Image, on_delete=PROTECT)


class Occurrence(PolymorphicModel, TaggableModel):
    """Something that happened"""
    searchable_fields = ['summary', 'description', 'related_topics__key', 'related_topics__aliases']

    summary = HTMLField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    date = HistoricDateField(null=True, blank=True)
    year = models.ForeignKey(Year, null=True, blank=True, on_delete=PROTECT, related_name='occurrences')
    locations = ManyToManyField('places.Place', through='OccurrenceLocation', related_name='occurrences', blank=True)
    related_quotes = ManyToManyField('quotes.Quote', through='OccurrenceQuoteRelation', symmetrical=True,
                                     related_name='related_occurrences', blank=True)
    sources = ManyToManyField(Source, through='OccurrenceSourceReference', blank=True)
    images = ManyToManyField(Image, related_name='occurrences', through=OccurrenceImage, blank=True)
    involved_entities = ManyToManyField('entities.Entity', related_name='involved_occurrences',
                                        through='OccurrenceEntityInvolvement', blank=True)
    period = models.ForeignKey('Duration', related_name='occurrences', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (('summary', 'date'),)
        ordering = ['-year__years_before_present', '-date']

    def __str__(self):
        return self.summary.text or "..."

    @property
    def description__truncated(self) -> SafeText:
        return mark_safe(truncatechars(self.description, 1200))

    @property
    def image(self) -> Optional[Image]:
        return (self.images.first() if self.images.exists() else
                self.involved_entities.first().image if self.involved_entities.exists() else None)

    @property
    def pretty_year(self) -> str:
        return str(self.year)

    def natural_key(self) -> Tuple:
        return self.summary, self.date

    def clean(self):
        attrs = (
            ('date', 'year'),
        )
        for date_attr, year_attr in attrs:
            date = getattr(self, date_attr)
            if date:
                year, _ = Year.objects.get_or_create(common_era=date.year)
                setattr(self, year_attr, year)
        else:
            if self.year and not self.date:
                pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Duration(Occurrence):
    """A duration of time over which something happens."""
    end_year = models.ForeignKey(Year, null=True, blank=True, on_delete=PROTECT, related_name='occurrences_ended')

    @property
    def pretty_year(self) -> str:
        return f'{self.year}–{self.end_year}'

    @property
    def years(self) -> QuerySet:
        return Year.objects.filter(common_era__gte=self.year.common_era, common_era__lte=self.end_year.common_era)


episode_types = (
    ('publication', 'Publication'),  # of book, article, etc.
    ('delivery', 'Delivery'),  # of speech, lecture, or letter
    ('writing', 'Writing'),  # of letter or historical document
    ('interview', 'Interview'),
    ('birth', 'Birth'),  # of person
    ('death', 'Death'),  # of person
    ('founding', 'Founding'),  # of organization
    ('battle', 'Battle'),
    ('other', 'Other')
)


class Episode(Occurrence):
    """A moment (or brief period) of time in which something happens."""
    type = models.CharField(max_length=12, choices=episode_types, default='other')
    date_is_precise = models.BooleanField(default=True)
    time_is_precise = models.BooleanField(default=False)


importance_options = (
    (1, 'Primary'),
    (2, 'Secondary'),
    (3, 'Tertiary'),
    (4, 'Quaternary'),
    (5, 'Quinary'),
    (6, 'Senary'),
    (7, 'Septenary'),
)


class OccurrenceLocation(Model):
    """A place being a site of an occurrence"""
    occurrence = models.ForeignKey(Occurrence, on_delete=CASCADE)
    location = models.ForeignKey('places.Place', related_name='location_occurrences', on_delete=CASCADE)
    importance = models.IntegerField(choices=importance_options, default=1)


class OccurrenceEntityInvolvement(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(Occurrence, on_delete=CASCADE)
    entity = models.ForeignKey('entities.Entity', related_name='occurrence_involvements', on_delete=CASCADE)
    importance = models.IntegerField(choices=importance_options, default=1)


class OccurrenceQuoteRelation(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(Occurrence, related_name='occurrence_quote_relations', on_delete=CASCADE)
    quote = models.ForeignKey('quotes.Quote', related_name='quote_occurrence_relations', on_delete=CASCADE)


class OccurrenceSourceReference(SourceReference):
    """A reference to a source."""
    occurrence = models.ForeignKey(Occurrence, related_name='source_references', on_delete=CASCADE)
    source = models.ForeignKey(Source, related_name='references_from_occurrences', on_delete=CASCADE)
