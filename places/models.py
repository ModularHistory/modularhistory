from typing import Tuple

from django.db import models
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from history.models import Model, PolymorphicModel


# from history.models import Model


class LocationTag(TaggedItemBase):
    """A place tag"""
    content_object = models.ForeignKey('Place', on_delete=models.CASCADE)


class Place(PolymorphicModel):
    """Where something has happened"""
    name = models.CharField(null=True, blank=True, max_length=40, unique=True)
    location = models.ForeignKey('places.Place', blank=True, null=True,
                                 related_name='places', on_delete=models.PROTECT)
    tags = TaggableManager(through=LocationTag, blank=True)

    def __str__(self):
        return self.name + (f', {self.location}' if self.location else '')

    # class Meta:
    #     unique_together = [['name',]]  # TODO

    def natural_key(self) -> Tuple:
        return self.name,


prepositions = (
    ('in', 'in'),
    ('at', 'at')
)


class Venue(Place):
    """A venue: a place where something happens (e.g., a university)"""
    preposition = models.CharField(max_length=2, choices=prepositions, default='in')

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
