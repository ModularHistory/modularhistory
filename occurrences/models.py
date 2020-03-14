from typing import List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import ManyToManyField, ForeignKey, CASCADE
from django.template.defaultfilters import truncatechars_html
from django.utils.safestring import SafeText, mark_safe
from django.core.exceptions import ValidationError
from history.fields import HistoricDateTimeField, HTMLField
from history.models import Model, PolymorphicModel, TaggableModel, DatedModel, SearchableMixin, SourceMixin
from images.models import Image
from sources.models import Source, SourceReference
from .manager import Manager


class OccurrenceImage(Model):
    occurrence = models.ForeignKey('Occurrence', related_name='occurrence_images', on_delete=CASCADE)
    image = models.ForeignKey(Image, on_delete=CASCADE)
    position = models.PositiveSmallIntegerField(
        default=1, blank=True,
        help_text='Set to 0 if the image is positioned manually.'
    )

    class Meta:
        unique_together = ['occurrence', 'image']
        ordering = ['position', 'image']

    def __str__(self):
        return mark_safe(f'{self.position}: {self.image.caption}')

    @property
    def key(self) -> str:
        return self.image.key

    def natural_key(self):
        return super().natural_key()
    natural_key.dependencies = ['images.image']


class OccurrenceChain(Model):
    description = HTMLField(max_length=200, null=True, unique=True)
    parent_chain = ForeignKey('self', on_delete=CASCADE, related_name='sub_chains')


class OccurrenceChainInclusion(Model):
    chain = ForeignKey(OccurrenceChain, on_delete=CASCADE, related_name='occurrence_inclusions')
    occurrence = ForeignKey('Occurrence', on_delete=CASCADE, related_name='chain_inclusions')

    class Meta:
        unique_together = ['chain', 'occurrence']


class Occurrence(DatedModel, TaggableModel, SearchableMixin, SourceMixin):
    """Something that happened"""
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)
    summary = HTMLField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    postscript = HTMLField(null=True, blank=True, help_text='Content to be displayed below all related data')
    locations = ManyToManyField('places.Place', through='OccurrenceLocation', related_name='occurrences', blank=True)
    related_quotes = ManyToManyField('quotes.Quote', through='OccurrenceQuoteRelation', symmetrical=True,
                                     related_name='related_occurrences', blank=True)
    sources = ManyToManyField(Source, through='OccurrenceSourceReference', related_name='occurrences', blank=True)
    images = ManyToManyField(Image, related_name='occurrences', through=OccurrenceImage, blank=True)
    involved_entities = ManyToManyField('entities.Entity', related_name='involved_occurrences',
                                        through='OccurrenceEntityInvolvement', blank=True)
    chains = ManyToManyField(OccurrenceChain, related_name='occurrences', through=OccurrenceChainInclusion)

    class Meta:
        unique_together = ['summary', 'date']
        ordering = ['-date']

    searchable_fields = [
        'summary', 'description', 'date__year',
        'involved_entities__name', 'involved_entities__aliases',
        'related_topics__key', 'related_topics__aliases'
    ]
    objects: Manager = Manager()

    def __str__(self):
        return self.summary.text or "..."

    @property
    def description__truncated(self) -> SafeText:
        return mark_safe(truncatechars_html(self.description, 250))

    @property
    def entity_images(self) -> Optional[List[Image]]:
        if self.involved_entities.exists():
            images = []
            for entity in self.involved_entities.all():
                if entity.images.exists():
                    if self.date:
                        image = entity.images.get_closest_to_datetime(self.date)
                        images.append(image)
            return images
        return None

    @property
    def image(self) -> Optional[Image]:
        if self.images.exists():
            return self.images.first()
        elif self.involved_entities.exists():
            for entity in self.involved_entities.all():
                if entity.images.exists():
                    if self.date:
                        return entity.images.get_closest_to_datetime(self.date)
                    return entity.image
        return None

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude, validate_unique)
        if not self.date:
            raise ValidationError('Occurrence needs a date.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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

    class Meta:
        unique_together = ['occurrence', 'location']


class OccurrenceEntityInvolvement(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(Occurrence, on_delete=CASCADE)
    entity = models.ForeignKey('entities.Entity', related_name='occurrence_involvements', on_delete=CASCADE)
    importance = models.PositiveSmallIntegerField(choices=importance_options, default=1)

    class Meta:
        unique_together = ['occurrence', 'entity']


class OccurrenceQuoteRelation(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(Occurrence, related_name='occurrence_quote_relations', on_delete=CASCADE)
    quote = models.ForeignKey('quotes.Quote', related_name='quote_occurrence_relations', on_delete=CASCADE)
    position = models.PositiveSmallIntegerField(default=1, blank=True)

    class Meta:
        unique_together = ['occurrence', 'quote']
        ordering = ['position', 'quote']

    def __str__(self):
        return mark_safe(f'{self.quote.source_reference}')


class OccurrenceSourceReference(SourceReference):
    """A reference to a source."""
    occurrence = models.ForeignKey(Occurrence, related_name='source_references', on_delete=CASCADE)
    source = models.ForeignKey(Source, related_name='references_from_occurrences', on_delete=CASCADE)

    class Meta:
        unique_together = [['occurrence', 'source', 'page_number', 'end_page_number'], ['occurrence', 'position']]
