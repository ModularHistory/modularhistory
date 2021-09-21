"""Classes for models with related entities."""

import logging
from typing import TYPE_CHECKING, Optional, Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.model import ExtendedModel
from core.models.model_with_cache import store
from core.models.relations.moderated import ModeratedPositionedRelation

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class AbstractLocationRelation(ModeratedPositionedRelation):
    """
    Abstract base model for locations relations.

    Models governing m2m relationships between `Place` and another model
    should inherit from this abstract model.
    """

    location = ManyToManyForeignKey(
        to='places.Place', related_name='%(app_label)s_%(class)s_set'
    )

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.location}'

    def content_object(self) -> models.ForeignKey:
        """Foreign key to the model that references the location."""
        raise NotImplementedError


class LocationsField(CustomManyToManyField):
    """Custom field for m2m relationship with locations."""

    target_model = 'places.Place'
    through_model_base = AbstractLocationRelation

    def __init__(self, through: Union[type[AbstractLocationRelation], str], **kwargs):
        """Construct the field."""
        kwargs['through'] = through
        kwargs['verbose_name'] = _('locations')
        super().__init__(**kwargs)


class ModelWithLocations(ExtendedModel):
    """A model that has one or more associated locations."""

    location_relations: 'Manager'

    class Meta:
        """Meta options for ModelWithLocations."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        abstract = True

    @property
    def locations(self) -> LocationsField:
        """
        Require implementation of a `locations` field on inheriting models.

        For example:
        ``
        locations = LocationsField(through=Location)
        ``
        """
        raise NotImplementedError

    @property
    def primary_location(self) -> Optional[dict]:
        """Return the location to represent the model instance by default."""
        try:
            return self.serialized_locations[0]
        except IndexError:
            logging.debug(f'No location could be retrieved for {self}')
            return None

    @property  # type: ignore
    @store(key='serialized_locations')
    def serialized_locations(self) -> list[dict]:
        """Return a list of dictionaries representing the instance's locations."""
        return [
            location_relation.location.serialize()
            for location_relation in self.location_relations.all().select_related('location')
        ]
