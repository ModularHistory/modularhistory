from typing import Any, Iterable, List, Optional

from django.core.exceptions import ValidationError
from django.db.models import ManyToManyField
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
from django.utils.safestring import SafeString

from django.core.exceptions import ObjectDoesNotExist
from images.models import Image
from modularhistory.fields import HTMLField, HistoricDateTimeField
from modularhistory.models import (
    DatedModel,
    ModelWithImages,
    ModelWithRelatedQuotes,
    ModelWithSources,
)
from modularhistory.utils.html import soupify
from occurrences.manager import OccurrenceManager
from occurrences.models.occurrence_image import OccurrenceImage
from quotes.models import quote_sorter_key

TRUNCATED_DESCRIPTION_LENGTH: int = 250


class Occurrence(DatedModel, ModelWithRelatedQuotes, ModelWithSources, ModelWithImages):
    """Something that happened."""

    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)
    summary = HTMLField(verbose_name='Summary', null=True, blank=True)
    description = HTMLField(verbose_name='Description', null=True, blank=True)
    postscript = HTMLField(
        verbose_name='Postscript',
        null=True,
        blank=True,
        help_text='Content to be displayed below all related data',
    )
    locations = ManyToManyField(
        'places.Place',
        through='occurrences.OccurrenceLocation',
        related_name='occurrences',
        blank=True,
    )
    images = ManyToManyField(
        Image,
        through='occurrences.OccurrenceImage',
        related_name='occurrences',
        blank=True,
    )
    occurrence_images: Any
    involved_entities = ManyToManyField(
        'entities.Entity',
        through='occurrences.OccurrenceEntityInvolvement',
        related_name='involved_occurrences',
        blank=True,
    )
    chains = ManyToManyField(
        'occurrences.OccurrenceChain',
        through='occurrences.OccurrenceChainInclusion',
        related_name='occurrences',
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
        'tags__topic__aliases',
    ]
    objects: OccurrenceManager = OccurrenceManager()  # type: ignore

    def __str__(self) -> str:
        """Return the string representation of the occurrence."""
        return self.summary.text or '...'

    def save(self, *args, **kwargs):
        """Save the occurrence to the database."""
        self.clean()
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

    def clean(self):
        """Prepare the occurrence to be saved."""
        super().clean()
        if not self.date:
            raise ValidationError('Occurrence needs a date.')

    @property
    def truncated_description(self) -> Optional[SafeString]:
        """Return the occurrence's description, truncated."""
        if not self.description:
            return None
        description = soupify(self.description.html)
        if description.find('img'):
            description.find('img').decompose()
        return format_html(
            truncatechars_html(description.prettify(), TRUNCATED_DESCRIPTION_LENGTH)
        )

    @property
    def ordered_images(self):
        """Careful!  These are occurrence-images, not images."""
        return self.occurrence_images.all().select_related('image')

    @property
    def unpositioned_images(self) -> Iterable[OccurrenceImage]:
        """Return the occurrence's images that are not manually positioned in HTML."""
        # 'unpositioned_images' is a little misleading; these are positioned
        # by their `position` attribute rather than manually positioned.
        unpositioned_images = self.ordered_images.filter(is_positioned=False)
        if unpositioned_images.exists():
            return unpositioned_images
        elif self.entity_images:
            unpositioned_images = self.entity_images
        elif self.primary_image:
            unpositioned_images = [self.primary_image]
        return unpositioned_images

    @property
    def entity_images(self) -> Optional[List[Image]]:
        """TODO: write docstring."""
        try:
            images = []
            for entity in self.involved_entities.all():
                if entity.images.exists():
                    if self.date:
                        image = entity.images.get_closest_to_datetime(self.date)
                        images.append(image)
            return images
        except (ObjectDoesNotExist, AttributeError):
            return None

    def get_context(self):
        """TODO: add docstring."""
        quotes = (
            [quote_relation.quote for quote_relation in self.quote_relations.all()]
            if self.quote_relations.exists()
            else []
        )
        return {
            'occurrence': self,
            'quotes': sorted(quotes, key=quote_sorter_key),
        }
