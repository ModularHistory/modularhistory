"""Classes for models with related entities."""

import logging
from typing import TYPE_CHECKING, Optional, Type, Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.fields.sorted_m2m_field import SortedManyToManyField
from core.models.model import Model
from core.models.model_with_cache import store
from core.models.positioned_relation import PositionedRelation

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class AbstractLocationRelation(PositionedRelation):
    """
    Abstract base model for locations relations.

    Models governing m2m relationships between `Place` and another model
    should inherit from this abstract model.
    """

    location = ManyToManyForeignKey(
        to='places.Place', related_name='%(app_label)s_%(class)s_set'
    )

    # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for AbstractLocationRelation."""

        abstract = True

    def content_object(self) -> models.ForeignKey:
        """Foreign key to the model that references the location."""
        raise NotImplementedError


class LocationsField(CustomManyToManyField):

    target_model = 'places.Place'
    through_model = AbstractLocationRelation

    def __init__(self, through: Union[Type[AbstractLocationRelation], str], **kwargs):
        kwargs['through'] = through
        kwargs['verbose_name'] = _('related quotes')
        super().__init__(**kwargs)


class ModelWithLocations(Model):
    """A model that has one or more associated locations."""

    locations = SortedManyToManyField(
        to='places.Place',
        related_name='_%(class)s_set',
        blank=True,
        verbose_name=_('locations'),
    )

    @property
    def _locations(self) -> LocationsField:
        raise NotImplementedError

    location_relations: 'Manager'

    class Meta:
        """Meta options for ModelWithLocations."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    @property
    def primary_location(self) -> Optional[dict]:
        """Return the location to represent the model instance by default."""
        try:
            return self.serialized_locations[0]
        except IndexError:
            logging.debug(f'No location could be retrieved for {self}')
            return None

    @property  # type: ignore
    @store(attribute_name='serialized_locations')
    def serialized_locations(self) -> list[dict]:
        """Return a list of dictionaries representing the instance's locations."""
        return [
            location_relation.location.serialize()
            for location_relation in self.location_relations.all().select_related(
                'location'
            )
        ]
