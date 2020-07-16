from typing import Any, List, Optional

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.db.models import ManyToManyField
from django.template.defaultfilters import truncatechars_html
from django.utils.safestring import SafeText, mark_safe

from history.fields import HistoricDateTimeField, HTMLField
from history.models import (
    TaggableModel, DatedModel,
    RelatedQuotesMixin, SearchableMixin, SourcesMixin
)
from images.models import Image
from quotes.models import quote_sorter_key
from ..manager import Manager


class Occurrence(DatedModel, TaggableModel, RelatedQuotesMixin, SourcesMixin, SearchableMixin):
    """Something that happened"""
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)
    summary = HTMLField(verbose_name='Summary', null=True, blank=True)
    description = HTMLField(verbose_name='Description', null=True, blank=True)
    postscript = HTMLField(verbose_name='Postscript', null=True, blank=True,
                           help_text='Content to be displayed below all related data')
    locations = ManyToManyField(
        'places.Place', through='occurrences.OccurrenceLocation',
        related_name='occurrences',
        blank=True
    )
    images = ManyToManyField(
        Image, related_name='occurrences',
        through='occurrences.OccurrenceImage',
        blank=True
    )
    occurrence_images: Any
    involved_entities = ManyToManyField(
        'entities.Entity', related_name='involved_occurrences',
        through='occurrences.OccurrenceEntityInvolvement', blank=True
    )
    chains = ManyToManyField(
        'occurrences.OccurrenceChain', related_name='occurrences',
        through='occurrences.OccurrenceChainInclusion'
    )

    class Meta:
        unique_together = ['summary', 'date']
        ordering = ['-date']

    searchable_fields = [
        'summary', 'description', 'date__year',
        'involved_entities__name', 'involved_entities__aliases',
        'tags__topic__key', 'tags__topic__aliases'
    ]
    objects: Manager = Manager()

    def __str__(self):
        return self.summary.text or '...'

    @property
    def description__truncated(self) -> Optional[SafeText]:
        if not self.description:
            return None
        description = BeautifulSoup(self.description.html, features='lxml')
        if description.find('img'):
            description.find('img').decompose()
        return mark_safe(truncatechars_html(description.prettify(), 250))

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
        quotes = ([quote_relation.quote for quote_relation in self.quote_relations.all()]
                  if self.quote_relations.exists() else [])
        return {
            'occurrence': self,
            'quotes': sorted(quotes, key=quote_sorter_key),
            # 'unpositioned_images' is a little misleading;
            # these are positioned by their `position` attribute rather than manually positioned.
            'unpositioned_images': [image for image in self.occurrence_images.all()
                                    if not image.is_positioned]
        }

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
