from typing import List

from django.db import models

from apps.places.models.base import Place, PlaceTypes

# Ordered list of location scopes (from specific to broad)
LOCATION_PRECEDENCE = [
    PlaceTypes.venue,
    PlaceTypes.city,
    PlaceTypes.county,
    PlaceTypes.state,
    PlaceTypes.country,
    PlaceTypes.region,
    PlaceTypes.continent,
]


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


class Venue(Place):
    """A specific place where something happens (e.g., a university)."""

    class Meta:
        """Meta options for Venue."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    location__type__in=get_allowable_location_types(PlaceTypes.venue)
                ),
                name='location_is_allowable',
            ),
        ]


class City(Place):
    """A city."""

    class Meta:
        """Meta options for City."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Cities'


class County(Place):
    """A county."""

    class Meta:
        """Meta options for County."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Counties'


class State(Place):
    """A state."""

    class Meta:
        """Meta options for State."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'States'


class Region(Place):
    """A region."""

    class Meta:
        """Meta options for Region."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Regions'


class Country(Place):
    """A country."""

    class Meta:
        """Meta options for Country."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Countries'


class Continent(Place):
    """A continent."""

    class Meta:
        """Meta options for Continent."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Continents'
