from typing import Any, List, Optional

from django.core.exceptions import ValidationError
from django.db.models import ManyToManyField
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
from django.utils.safestring import SafeString

from images.models import Image
from modularhistory.fields import HTMLField, HistoricDateTimeField
from modularhistory.models import DatedModel, ModelWithImages, ModelWithRelatedQuotes, ModelWithSources
from modularhistory.utils import soupify
from occurrences.manager import OccurrenceManager
from occurrences.models.occurrence_image import OccurrenceImage
from quotes.models import quote_sorter_key

TRUNCATED_DESCRIPTION_LENGTH: int = 250


class Occurrence(DatedModel, ModelWithRelatedQuotes, ModelWithSources, ModelWithImages):
    """Something that happened."""

    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)
    summary = HTMLField(
        verbose_name='Summary',
        null=True,
        blank=True
    )
    description = HTMLField(
        verbose_name='Description',
        null=True,
        blank=True
    )
    postscript = HTMLField(
        verbose_name='Postscript',
        null=True,
        blank=True,
        help_text='Content to be displayed below all related data'
    )
    locations = ManyToManyField(
        'places.Place',
        through='occurrences.OccurrenceLocation',
        related_name='occurrences',
        blank=True
    )
    images = ManyToManyField(
        Image,
        through='occurrences.OccurrenceImage',
        related_name='occurrences',
        blank=True
    )
    occurrence_images: Any
    involved_entities = ManyToManyField(
        'entities.Entity',
        through='occurrences.OccurrenceEntityInvolvement',
        related_name='involved_occurrences',
        blank=True
    )
    chains = ManyToManyField(
        'occurrences.OccurrenceChain',
        through='occurrences.OccurrenceChainInclusion',
        related_name='occurrences'
    )

    class Meta:
        unique_together = ['summary', 'date']
        ordering = ['-date']

    searchable_fields = [
        'summary',
        'description',
        'date__year',
        'involved_entities__name',
        'involved_entities__aliases',
        'tags__topic__key',
        'tags__topic__aliases'
    ]
    objects: OccurrenceManager = OccurrenceManager()

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.summary.text or '...'

    @property
    def truncated_description(self) -> Optional[SafeString]:
        """TODO: write docstring."""
        if not self.description:
            return None
        description = soupify(self.description.html)
        if description.find('img'):
            description.find('img').decompose()
        return format_html(
            truncatechars_html(description.prettify(), TRUNCATED_DESCRIPTION_LENGTH)
        )

    @property
    def entity_images(self) -> Optional[List[Image]]:
        """TODO: write docstring."""
        if self.involved_entities.exists():
            images = []
            for entity in self.involved_entities.all():
                if entity.images.exists():
                    if self.date:
                        image = entity.images.get_closest_to_datetime(self.date)
                        images.append(image)
            return images
        return None

    def full_clean(self, exclude=None, validate_unique=True):
        """TODO: add docstring."""
        super().full_clean(exclude, validate_unique)
        if not self.date:
            raise ValidationError('Occurrence needs a date.')

    def get_context(self):
        """TODO: add docstring."""
        quotes = (
            [quote_relation.quote for quote_relation in self.quote_relations.all()]
            if self.quote_relations.exists() else []
        )
        return {
            'occurrence': self,
            'quotes': sorted(quotes, key=quote_sorter_key),
            # 'unpositioned_images' is a little misleading;
            # these are positioned by their `position` attribute rather than manually positioned.
            'unpositioned_images': [
                image for image in self.occurrence_images.all()
                if not image.is_positioned
            ]
        }

    def save(self, *args, **kwargs):
        """TODO: add docstring."""
        self.full_clean()
        super().save(*args, **kwargs)
        if not self.images.exists():
            image = None
            if self.involved_entities.exists():
                for entity in self.involved_entities.all():
                    if entity.images.exists():
                        if self.date:
                            image = entity.images.get_closest_to_datetime(self.date)
                        else:
                            image = entity.image
            if image:
                OccurrenceImage.objects.create(occurrence=self, image=image)
