from django.db import models

from history.models import Model, TypedModel

prepositions = (
    ('in', 'in'),
    ('at', 'at')
)


class Place(TypedModel, Model):
    """Where something has happened."""

    name = models.CharField(null=True, blank=True, max_length=40, unique=True)
    location = models.ForeignKey(
        'self',
        related_name='places',
        blank=True, null=True,
        on_delete=models.PROTECT
    )
    preposition = models.CharField(max_length=2, choices=prepositions, default='in')

    class Meta:
        unique_together = ['name', 'location']

    def __str__(self) -> str:
        """TODO: write docstring."""
        location = self.location
        return self.name + (f', {location}' if location else '')

    @property
    def string(self) -> str:
        """Presentable string to display in HTML."""
        location = self.location
        # Don't append the location's location if it's a continent, a region, or the USA.
        # TODO: This is hacky; maybe it can be improved.
        if (isinstance(location, (Region, Continent))
                or isinstance(location, Country) and location.name == 'United States of America'):
            location = None
        return self.name + (f', {location.name}' if location else '')


class Venue(Place):
    """A specific place where something happens (e.g., a university)."""

    class Meta:
        verbose_name_plural = 'Venues'


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

    pass


class Region(Place):
    """A region."""

    pass


class Country(Place):
    """A country."""

    class Meta:
        verbose_name_plural = 'Countries'


class Continent(Place):
    """A continent."""

    pass
