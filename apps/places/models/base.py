from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.model import TypedModel
from core.models.model_with_cache import ModelWithCache, store

PREPOSITION_CHOICES = (('in', 'in'), ('at', 'at'))


class PlaceTypes:
    """Constants for location types."""

    venue = 'places.venue'
    city = 'places.city'
    county = 'places.county'
    state = 'places.state'
    country = 'places.country'
    region = 'places.region'
    continent = 'places.continent'


NAME_MAX_LENGTH: int = 40


class Place(TypedModel, ModelWithCache):
    """Where something has happened."""

    name = models.CharField(
        verbose_name=_('name'),
        null=True,
        blank=True,
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )
    location = models.ForeignKey(
        to='self',
        related_name='places',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    preposition = models.CharField(
        max_length=2, choices=PREPOSITION_CHOICES, default='in'
    )

    class Meta:
        unique_together = ['name', 'location']

    slug_base_field = 'string'

    def __str__(self) -> str:
        """Return the location's string representation."""
        return self.string

    def save(self):
        """Save the place to the database."""
        if self.type == 'places.place' or not self.type:
            raise ValidationError('Place must have a type.')
        else:
            # Prevent a RuntimeError when saving a new place
            self.recast(self.type)
        super().save()

    @property  # type: ignore
    @store(attribute_name='string')
    def string(self) -> str:
        """Presentable string to display in HTML."""
        location = self.location
        # TODO: This is hacky; maybe it can be improved.
        # Don't append the location's location if it's a continent, region, or inferable country
        if location:
            inferable_countries = ['United States of America']
            location_is_inferable_country = (
                location.type == PlaceTypes.country
                and location.name in inferable_countries
            )
            location_is_inferable = location_is_inferable_country or location.type in {
                PlaceTypes.region,
                PlaceTypes.continent,
            }
            if location_is_inferable:
                location = None
        components = [self.name, location.name if location else '']
        return ', '.join([component for component in components if component])
