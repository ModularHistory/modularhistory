from typing import TYPE_CHECKING, Optional

from django.core.exceptions import ValidationError
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.propositions.api.serializers import OccurrenceSerializer
from apps.propositions.models.proposition import PolymorphicProposition
from core.models.manager import Manager
from core.utils.html import soupify

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from apps.entities.models.entity import Entity
    from apps.images.models.image import Image


TRUNCATED_DESCRIPTION_LENGTH: int = 250


class OccurrenceManager(Manager):
    """Manager for occurrences."""

    def get_queryset(self) -> 'QuerySet[Occurrence]':
        """Return the propositions of type `propositions.occurrence`."""
        return super().get_queryset().filter(type='propositions.occurrence')


class Occurrence(PolymorphicProposition):
    """
    An occurrence, i.e., something that has happened.

    For our purposes, an occurrence is a proposition: each occurrence is proposed
    (with some degree of certainty) to have occurred. As such, this model inherits
    from `Proposition`.
    """

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for the `Occurrence` model."""

        proxy = True
        ordering = ['date']

    objects = OccurrenceManager()
    searchable_fields = [
        'summary',
        'elaboration',
        'date__year',
        'related_entities__name',
        'related_entities__aliases',
        'tags__key',
        'tags__aliases',
    ]
    serializer = OccurrenceSerializer

    def __str__(self) -> str:
        """Return the string representation of the occurrence."""
        return self.summary

    def save(self, *args, **kwargs):
        """Save the occurrence to the database."""
        super().save(*args, **kwargs)
        if not self.images.exists():
            image: Optional['Image'] = None
            if self.related_entities.exists():
                entity: 'Entity'
                for entity in self.related_entities.all():
                    if entity.images.exists():
                        if self.date:
                            image = entity.images.get_closest_to_datetime(self.date)
                        else:
                            image = entity.image
            if image:
                self.images.add(image)

    def clean(self):
        """Prepare the occurrence to be saved."""
        super().clean()
        if not self.date:
            raise ValidationError('Occurrence needs a date.')

    @property
    def truncated_elaboration(self) -> Optional[SafeString]:
        """Return the occurrence's elaboration, truncated."""
        if not self.elaboration:
            return None
        elaboration = soupify(self.elaboration)
        if elaboration.find('img'):
            elaboration.find('img').decompose()
        truncated_elaboration = (
            truncatechars_html(elaboration.prettify(), TRUNCATED_DESCRIPTION_LENGTH)
            .replace('<p>', '')
            .replace('</p>', '')
        )
        return format_html(truncated_elaboration)

    @property
    def ordered_images(self) -> 'QuerySet':
        """Careful!  These are occurrence-images, not images."""
        return self.image_relations.all().select_related('image')


class Birth(Occurrence):
    """A birth of an entity."""

    class Meta:
        proxy = True


class Death(Occurrence):
    """A death of an entity."""

    class Meta:
        proxy = True


class Publication(Occurrence):
    """A publication of a source."""

    class Meta:
        proxy = True


class Speech(Occurrence):
    """A speech."""

    class Meta:
        proxy = True
