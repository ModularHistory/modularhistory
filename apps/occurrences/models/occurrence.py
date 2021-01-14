from typing import TYPE_CHECKING, Optional

from concurrency.fields import IntegerVersionField
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.images.models.model_with_images import ModelWithImages
from apps.occurrences.manager import OccurrenceManager
from apps.occurrences.models.occurrence_image import OccurrenceImage
from apps.occurrences.serializers import OccurrenceSerializer
from apps.quotes.models import quote_sorter_key
from apps.quotes.models.model_with_related_quotes import ModelWithRelatedQuotes
from apps.search.models import SearchableDatedModel
from apps.sources.models.model_with_sources import ModelWithSources
from modularhistory.fields import HistoricDateTimeField, HTMLField
from modularhistory.utils.html import soupify

if TYPE_CHECKING:
    from django.db.models.manager import Manager

TRUNCATED_DESCRIPTION_LENGTH: int = 250


class Occurrence(
    SearchableDatedModel,
    ModelWithRelatedQuotes,
    ModelWithSources,
    ModelWithImages,
):
    """Something that happened."""

    date = HistoricDateTimeField(verbose_name=_('date'), null=True, blank=True)
    end_date = HistoricDateTimeField(verbose_name=_('end date'), null=True, blank=True)
    summary = HTMLField(verbose_name=_('summary'), paragraphed=False)
    description = HTMLField(verbose_name=_('description'), paragraphed=True)
    postscript = HTMLField(
        verbose_name=_('postscript'),
        null=True,
        blank=True,
        paragraphed=True,
        help_text='Content to be displayed below all related data',
    )
    version = IntegerVersionField()

    locations = models.ManyToManyField(
        to='places.Place',
        through='occurrences.OccurrenceLocation',
        related_name='occurrences',
        blank=True,
        verbose_name=_('locations'),
    )
    images = models.ManyToManyField(
        to='images.Image',
        through='occurrences.OccurrenceImage',
        related_name='occurrences',
        blank=True,
        verbose_name=_('images'),
    )
    image_relations: 'Manager'
    involved_entities = models.ManyToManyField(
        to='entities.Entity',
        through='occurrences.OccurrenceEntityInvolvement',
        related_name='involved_occurrences',
        blank=True,
        verbose_name=_('involved entities'),
    )
    chains = models.ManyToManyField(
        to='occurrences.OccurrenceChain',
        through='occurrences.OccurrenceChainInclusion',
        related_name='occurrences',
        verbose_name=_('chains'),
    )

    class Meta:
        """
        Meta options for the Category model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        unique_together = ['summary', 'date']
        ordering = ['-date']

    objects: OccurrenceManager = OccurrenceManager()  # type: ignore
    searchable_fields = [
        'summary',
        'description',
        'date__year',
        'involved_entities__name',
        'involved_entities__aliases',
        'tags__topic__key',
        'tags__topic__aliases',
    ]
    serializer = OccurrenceSerializer
    slug_base_field = 'summary'

    def __str__(self) -> str:
        """Return the string representation of the occurrence."""
        return self.summary.text

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
        return self.image_relations.all().select_related('image')

    def get_context(self):
        """Return context for rendering the occurrence's detail template."""
        quotes = [
            quote_relation.quote
            for quote_relation in self.quote_relations.all()
            .select_related('quote')
            .iterator()
        ]
        return {
            'occurrence': self,
            'quotes': sorted(quotes, key=quote_sorter_key),
        }
