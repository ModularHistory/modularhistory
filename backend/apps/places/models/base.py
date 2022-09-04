from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.model_with_cache import store
from core.models.module import TypedModule

NAME_MAX_LENGTH: int = 40
PREPOSITION_CHOICES = (('in', 'in'), ('at', 'at'))


class PlaceTypes:
    """Constants for location types."""

    venue = 'places.venue'
    city = 'places.city'
    county = 'places.county'
    state = 'places.state'
    administrative_division = 'places.administrativedivision'
    country = 'places.country'
    region = 'places.region'
    continent = 'places.continent'


# Ordered list of location scopes (from specific to broad)
LOCATION_PRECEDENCE = [
    PlaceTypes.venue,
    PlaceTypes.city,
    PlaceTypes.county,
    PlaceTypes.state,
    PlaceTypes.administrative_division,
    PlaceTypes.country,
    PlaceTypes.region,
    PlaceTypes.continent,
]


def get_allowable_location_types(reference_location_type: str) -> list[str]:
    """
    Given a location type, return the allowable parent location types.

    For example, if reference_location_type is "places.country", return
    ["places.region", "places.continent"]
    """
    allowable_types: list[str] = []
    for location_type in reversed(LOCATION_PRECEDENCE):
        if location_type == reference_location_type:
            return allowable_types
        allowable_types.append(location_type)
    return allowable_types


class Place(TypedModule):
    """Where something has happened."""

    name = models.CharField(
        verbose_name=_('name'),
        blank=False,
        max_length=NAME_MAX_LENGTH,
    )
    location = models.ForeignKey(
        to='self',
        related_name='places',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    preposition = models.CharField(max_length=2, choices=PREPOSITION_CHOICES, default='in')

    class Meta:
        unique_together = ['name', 'location']

    slug_base_fields = ('string',)

    def __str__(self) -> str:
        """Return the location's string representation."""
        return self.string

    def save(self, *args, **kwargs):
        """Save the place to the database."""
        if self.type == 'places.place' or not self.type:
            raise ValidationError('Place must have a type.')
        else:
            # Prevent a RuntimeError when saving a new place
            self.recast(self.type)
        location: Optional['Place'] = self.location
        if location:
            if location.type not in get_allowable_location_types(self.type):
                raise ValidationError(
                    f'{self} cannot have a parent location of type {location.type}.'
                )
        super().save(*args, **kwargs)

    def get_default_title(self) -> str:
        """Return the value the title should be set to, if not manually set."""
        return self.name

    @property  # type: ignore
    @store(key='string')
    def string(self) -> str:
        """Presentable string to display in HTML."""
        location = self.location
        # TODO: This is hacky; maybe it can be improved.
        # Don't append the location's location if it's a continent, region, or inferable country
        if location:
            inferable_countries = ['United States of America']
            location_is_inferable_country = (
                location.type == PlaceTypes.country and location.name in inferable_countries
            )
            location_is_inferable = location_is_inferable_country or location.type in {
                PlaceTypes.region,
                PlaceTypes.continent,
            }
            if location_is_inferable:
                location = None
        components = [self.name, location.name if location else '']
        return ', '.join([component for component in components if component])
