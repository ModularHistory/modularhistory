from django.db import models

from history.models import Model, TypedModel

prepositions = (
    ('in', 'in'),
    ('at', 'at')
)


class Place(TypedModel):
    """Where something has happened"""
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

    def __str__(self):
        return self.name + (f', {self.location}' if self.location else '')


class Venue(Place):
    """A venue: a place where something happens (e.g., a university)"""
    class Meta:
        verbose_name_plural = 'Venues'


class City(Place):
    """A city"""
    class Meta:
        verbose_name_plural = 'Cities'


class County(Place):
    """A city"""
    class Meta:
        verbose_name_plural = 'Counties'


class State(Place):
    """A state"""
    pass


class Region(Place):
    """A region"""
    pass


class Country(Place):
    """A country"""
    class Meta:
        verbose_name_plural = 'Countries'


class Continent(Place):
    """A continent"""
    pass
