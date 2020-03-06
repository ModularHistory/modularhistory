from typing import List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import ManyToManyField, ForeignKey, CASCADE
from django.template.defaultfilters import truncatechars_html
from django.utils.safestring import SafeText, mark_safe
from taggit.models import TaggedItemBase

from history.fields.historic_datetime_field import HistoricDateTimeField
from history.fields.html_field import HTMLField
from history.models import Model, PolymorphicModel, TaggableModel, DatedModel, SearchableMixin
from images.models import Image
from sources.models import Source, SourceReference
from .manager import Manager


class OccurrenceImage(Model):
    occurrence = models.ForeignKey('Occurrence', related_name='occurrence_images', on_delete=CASCADE)
    image = models.ForeignKey(Image, on_delete=CASCADE)
    position = models.PositiveSmallIntegerField(default=1, blank=True,
                                                help_text='Set to 0 if the image is positioned manually.')

    class Meta:
        unique_together = ['occurrence', 'image']
        ordering = ['position', 'image']

    def __str__(self):
        return mark_safe(f'{self.position}: {self.image.caption}')

    @property
    def key(self) -> str:
        return self.image.key


class OccurrenceChain(Model):
    parent_chain = ForeignKey('self', on_delete=CASCADE, related_name='sub_chains')


class OccurrenceChainInclusion(Model):
    chain = ForeignKey(OccurrenceChain, on_delete=CASCADE, related_name='occurrence_inclusions')
    occurrence = ForeignKey('Occurrence', on_delete=CASCADE, related_name='chain_inclusions')

    class Meta:
        unique_together = ['chain', 'occurrence']


class Occurrence(DatedModel, TaggableModel, SearchableMixin):
    """Something that happened"""
    objects: Manager = Manager()

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
        unique_together = (('summary', 'date'),)
        ordering = ['-date']

    searchable_fields = ['summary', 'description', 'date__year',
                         'involved_entities__name', 'involved_entities__aliases',
                         'related_topics__key', 'related_topics__aliases']

    def __str__(self):
        return self.summary.text or "..."

    @property
    def description__truncated(self) -> SafeText:
        return mark_safe(truncatechars_html(self.description, 1000))

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

    @property
    def source_reference(self) -> Optional['OccurrenceSourceReference']:
        if not len(self.sources.all()):
            return None
        return self.source_references.order_by('position')[0]

    def natural_key(self) -> Tuple:
        return self.summary, self.date

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude, validate_unique)
        # ois = list(self.occurrence_images.order_by('position'))
        # for i, oi in enumerate(ois):
        #     if i < len(ois)-1 and not oi.position == 0:
        #         if oi.position == ois[i+1].position:
        #             raise ValidationError(f'{oi} has same position as {ois[i+1]}: {oi.position}. '
        #                                   f'Positions should be unique.')

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
        unique_together = ['occurrence', 'source']
