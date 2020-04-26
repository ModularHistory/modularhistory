from typing import Any, List, Optional

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE
from django.template.defaultfilters import truncatechars_html
from django.utils.safestring import SafeText, mark_safe

from entities.models import Entity
from history.fields import HistoricDateTimeField, HTMLField
from history.models import (Model, PolymorphicModel, TaggableModel,
                            DatedModel, SearchableMixin, SourceMixin)
from images.models import Image
from quotes.models import quote_sorter_key
from sources.models import Source, Citation
from .manager import Manager


class OccurrenceImage(Model):
    occurrence = models.ForeignKey(
        'Occurrence', related_name='occurrence_images',
        on_delete=CASCADE
    )
    image = models.ForeignKey(Image, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Set to 0 if the image is positioned manually.'
    )

    class Meta:
        unique_together = ['occurrence', 'image']
        ordering = ['position', 'image']

    def __str__(self):
        return mark_safe(f'{self.position}: {self.image.caption}')

    @property
    def is_positioned(self) -> bool:
        return f'image: {self.image.pk}' in self.occurrence.description.raw_value

    @property
    def image_pk(self) -> str:
        return self.image.pk

    @property
    def key(self) -> str:
        return self.image.key


class OccurrenceChain(Model):
    description = HTMLField(max_length=200, null=True, unique=True)
    parent_chain = ForeignKey('self', on_delete=CASCADE, related_name='sub_chains')


class OccurrenceChainInclusion(Model):
    chain = ForeignKey(OccurrenceChain, on_delete=CASCADE, related_name='occurrence_inclusions')
    occurrence = ForeignKey('Occurrence', on_delete=CASCADE, related_name='chain_inclusions')

    class Meta:
        unique_together = ['chain', 'occurrence']


class Occurrence(SourceMixin, SearchableMixin, DatedModel, TaggableModel):
    """Something that happened"""
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)
    summary = HTMLField(verbose_name='Summary', null=True, blank=True)
    description = HTMLField(verbose_name='Description', null=True, blank=True)
    postscript = HTMLField(verbose_name='Postscript', null=True, blank=True,
                           help_text='Content to be displayed below all related data')
    locations = ManyToManyField(
        'places.Place', through='OccurrenceLocation',
        related_name='occurrences',
        blank=True
    )
    related_quotes = ManyToManyField(
        'quotes.Quote', through='OccurrenceQuoteRelation',
        symmetrical=True,
        related_name='related_occurrences',
        blank=True
    )
    images = ManyToManyField(
        Image, related_name='occurrences',
        through=OccurrenceImage,
        blank=True
    )
    occurrence_images: Any
    involved_entities = ManyToManyField(
        'entities.Entity', related_name='involved_occurrences',
        through='OccurrenceEntityInvolvement', blank=True
    )
    chains = ManyToManyField(
        OccurrenceChain, related_name='occurrences',
        through=OccurrenceChainInclusion
    )

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
        return self.summary.text or '...'

    @property
    def description__truncated(self) -> Optional[SafeText]:
        if not self.description:
            return None
        return mark_safe(truncatechars_html(self.description.html, 250))

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

    def get_context(self):
        return {
            'occurrence': self,
            'quotes': sorted(self.related_quotes.all(), key=quote_sorter_key),
            # 'unpositioned_images' is a little misleading;
            # these are positioned by their `position` attribute rather than manually positioned.
            'unpositioned_images': [image for image in self.occurrence_images.all()
                                    if not image.is_positioned]
        }

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
    location = models.ForeignKey(
        'places.Place', related_name='location_occurrences',
        on_delete=CASCADE
    )
    importance = models.IntegerField(choices=importance_options, default=1)

    class Meta:
        unique_together = ['occurrence', 'location']


class OccurrenceEntityInvolvement(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(Occurrence, on_delete=CASCADE)
    entity = models.ForeignKey(
        'entities.Entity', related_name='occurrence_involvements',
        on_delete=CASCADE
    )
    importance = models.PositiveSmallIntegerField(choices=importance_options, default=1)

    class Meta:
        unique_together = ['occurrence', 'entity']

    def __str__(self) -> SafeText:
        return mark_safe(f'{self.occurrence.date_string}: {self.occurrence.summary}')


class OccurrenceQuoteRelation(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(
        Occurrence, related_name='occurrence_quote_relations',
        on_delete=CASCADE
    )
    quote = models.ForeignKey(
        'quotes.Quote', related_name='quote_occurrence_relations',
        on_delete=CASCADE
    )
    position = models.PositiveSmallIntegerField(null=True, blank=True)  # TODO: add cleaning logic

    class Meta:
        unique_together = ['occurrence', 'quote']
        ordering = ['position', 'quote']

    def __str__(self):
        return mark_safe(f'{self.quote.citation}')

    @property
    def quote_pk(self) -> str:
        return self.quote.pk
