from typing import List

from django.db import models

from modularhistory.models import Model, TypedModel

PREPOSITION_CHOICES = (
    ('in', 'in'),
    ('at', 'at')
)

# Constants for location types
VENUE = 'places.venue'
CITY = 'places.city'
COUNTY = 'places.county'
STATE = 'places.state'
COUNTRY = 'places.country'
REGION = 'places.region'
CONTINENT = 'places.continent'

# Ordered list of location scopes (from specific to broad)
LOCATION_PRECEDENCE = [
    VENUE,
    CITY,
    COUNTY,
    STATE,
    COUNTRY,
    REGION,
    CONTINENT
]

NAME_MAX_LENGTH: int = 40


def get_allowable_location_types(reference_location_type: str) -> List[str]:
    """
    Given a location type, return the allowable parent location types.

    For example, if reference_location_type is "places.country", return
    ["places.region", "places.continent"]
    """
    allowable_types: List[str] = []
    for location_type in reversed(LOCATION_PRECEDENCE):
        if location_type == reference_location_type:
            return allowable_types
        allowable_types.append(location_type)
    return allowable_types


class Place(TypedModel, Model):
    """Where something has happened."""

    name = models.CharField(
        null=True,
        blank=True,
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    location = models.ForeignKey(
        'self',
        related_name='places',
        blank=True, null=True,
        on_delete=models.PROTECT
    )
    preposition = models.CharField(
        max_length=2,
        choices=PREPOSITION_CHOICES,
        default='in'
    )

    class Meta:
        unique_together = ['name', 'location']

    def __str__(self) -> str:
        """TODO: write docstring."""
        components = [
            self.name,
            f'{self.location if self.location else ""}'
        ]
        components = [component for component in components if component]
        return ', '.join(components)

    @property
    def string(self) -> str:
        """Presentable string to display in HTML."""
        location = self.location
        # TODO: This is hacky; maybe it can be improved.
        # Don't append the location's location if it's a continent, a region, or an inferrable country
        if location:
            inferrable_countries = ['United States of America']
            location_is_inferrable_country = (
                isinstance(location, Country) and
                location.name in inferrable_countries
            )
            location_is_inferrable = (
                location_is_inferrable_country or
                isinstance(location, (Region, Continent))
            )
            if location_is_inferrable:
                location = None
        components = [self.name, location.name if location else '']
        components = [component for component in components if component]
        return ', '.join(components)


class Venue(Place):
    """A specific place where something happens (e.g., a university)."""

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(location__type__in=get_allowable_location_types(VENUE)),
                name='location_is_allowable'
            ),
        ]


class City(Place):
    """A city."""

    class Meta:
        verbose_name_plural = 'Cities'


class County(Place):
    """A county."""

    class Meta:
        verbose_name_plural = 'Counties'


class State(Place):
    """A state."""

    class Meta:
        verbose_name_plural = 'States'


class Region(Place):
    """A region."""

    class Meta:
        verbose_name_plural = 'Regions'


class Country(Place):
    """A country."""

    class Meta:
        verbose_name_plural = 'Countries'


class Continent(Place):
    """A continent."""

    class Meta:
        verbose_name_plural = 'Continents'
