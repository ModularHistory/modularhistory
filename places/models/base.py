from django.db import models

from modularhistory.models import ModelWithComputations, TypedModel, retrieve_or_compute

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


class Place(TypedModel, ModelWithComputations):
    """Where something has happened."""

    name = models.CharField(
        null=True, blank=True, max_length=NAME_MAX_LENGTH, unique=True
    )
    location = models.ForeignKey(
        'self', related_name='places', blank=True, null=True, on_delete=models.PROTECT
    )
    preposition = models.CharField(
        max_length=2, choices=PREPOSITION_CHOICES, default='in'
    )

    class Meta:
        unique_together = ['name', 'location']

    class FieldNames(ModelWithComputations.FieldNames):
        name = 'name'
        location = 'location'

    slug_base_field = 'string'

    def __str__(self) -> str:
        """Return the location's string representation."""
        return self.string

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='string')
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
