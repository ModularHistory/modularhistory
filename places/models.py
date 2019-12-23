from django.db import models
from polymorphic.models import PolymorphicModel


class Location(PolymorphicModel):
    """Where something has happened"""
    name = models.CharField(null=True, blank=True, max_length=40)
    location = models.ForeignKey('places.Location', blank=True, null=True,
                                 related_name='locations', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name}'


class City(Location):
    """A city"""

    class Meta:
        verbose_name_plural = 'Cities'


class County(Location):
    """A city"""

    class Meta:
        verbose_name_plural = 'Counties'


class State(Location):
    """A state"""
    pass


class Region(Location):
    """A region"""
    pass


class Country(Location):
    """A country"""

    class Meta:
        verbose_name_plural = 'Countries'


class Continent(Location):
    """A continent"""
    pass
