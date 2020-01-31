from datetime import datetime
from typing import Optional

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE, SET_NULL
from django.template.defaultfilters import truncatechars
from django.utils.safestring import SafeText, mark_safe

from history.fields import HTMLField, ArrayField, HistoricDateField, HistoricDateTimeField
from history.models import Model, PolymorphicModel, TaggableModel
from images.models import Image


class EntityImage(Model):
    entity = ForeignKey('Entity', related_name='entity_images', on_delete=CASCADE)
    image = ForeignKey(Image, related_name='image_entities', on_delete=CASCADE)


class Entity(PolymorphicModel, TaggableModel):
    """An entity"""
    name = models.CharField(max_length=100)
    aliases = ArrayField(
        models.CharField(max_length=100),
        null=True, blank=True
    )
    description = HTMLField(null=True, blank=True)
    birth_date = HistoricDateTimeField(null=True, blank=True)
    death_date = HistoricDateTimeField(null=True, blank=True)
    is_living = models.BooleanField(default=False)
    images = ManyToManyField(Image, through=EntityImage, related_name='entities', blank=True)

    searchable_fields = ['name', 'aliases', 'description']

    class Meta:
        verbose_name_plural = 'Entities'
        ordering = ['name', 'birth_date']

    def __str__(self):
        return f'{self.name}'

    @property
    def image(self) -> Optional[Image]:
        return (self.images.first() if self.images.exists()
                else None)

    @property
    def has_quotes(self) -> bool:
        return bool(len(self.quotes.all()))

    @property
    def description__truncated(self) -> SafeText:
        return mark_safe(truncatechars(self.description, 1200))

    def natural_key(self):
        return self.name, self.birth_date, self.death_date


class Person(Entity):
    """A person"""
    occupations = ManyToManyField('Occupation', related_name='participants', blank=True)
    affiliations = ManyToManyField('Organization', related_name='members', through='Affiliation', blank=True)

    class Meta:
        verbose_name_plural = 'People'


class Occupation(Model):
    name = models.CharField(max_length=50)
    description = HTMLField(null=True, blank=True)
    classification = ForeignKey('OccupationClassification', related_name='occupations', null=True, blank=True,
                                on_delete=SET_NULL)

    def __str__(self):
        return self.name


class OccupationClassification(Model):
    name = models.CharField(max_length=50)
    description = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.name


class _Engagement(Model):
    start_date = HistoricDateField(null=True, blank=True)
    end_date = HistoricDateField(null=True, blank=True)

    class Meta:
        abstract = True


class OccupationEngagement(_Engagement):
    occupation = ForeignKey(Occupation, related_name='person_engagements', on_delete=CASCADE)
    person = ForeignKey(Person, related_name='occupation_engagements', on_delete=CASCADE)

    def __str__(self):
        return f'{self.person} — {self.occupation}'


class Affiliation(_Engagement):
    person = ForeignKey(Person, related_name='organization_affiliations', on_delete=CASCADE)
    organization = ForeignKey('Organization', related_name='person_affiliations', on_delete=CASCADE)
    roles = ManyToManyField('Role', related_name='affiliations', through='RoleFulfillment', blank=True)

    def __str__(self):
        return f'{self.person} — {self.organization}'


class RoleFulfillment(_Engagement):
    affiliation = ForeignKey(Affiliation, related_name='role_fulfillments', on_delete=CASCADE)
    role = ForeignKey('Role', related_name='fulfillments', on_delete=CASCADE)


class Role(Model):
    name = models.CharField(max_length=100)
    description = HTMLField(null=True, blank=True)
    organization = ForeignKey('Organization', related_name='roles', on_delete=CASCADE)

    def __str__(self):
        return self.name


class Organization(Entity):
    """An organization"""
    parent_organization = ForeignKey('self', related_name='child_organizations', null=True, blank=True,
                                     on_delete=SET_NULL)

    class Meta:
        verbose_name_plural = 'Organizations'

    @property
    def founding_date(self) -> datetime:
        return self.birth_date
