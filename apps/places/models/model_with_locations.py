"""Classes for models with related entities."""

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from django.utils.translation import ugettext_lazy as _

from core.fields.sorted_m2m_field import SortedManyToManyField
from core.models.model import Model
from core.models.model_with_cache import store

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class ModelWithLocations(Model):
    """A model that has one or more associated locations."""

    locations = SortedManyToManyField(
        to='places.Place',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('locations'),
    )

    location_relations: 'Manager'

    class Meta:
        """Meta options for ModelWithLocations."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    @property
    def primary_location(self) -> Optional[Dict]:
        """Return the location to represent the model instance by default."""
        try:
            return self.serialized_locations[0]
        except IndexError:
            logging.debug(f'No location could be retrieved for {self}')
            return None

    @property  # type: ignore
    @store(attribute_name='serialized_locations')
    def serialized_locations(self) -> List[Dict]:
        """Return a list of dictionaries representing the instance's locations."""
        return [
            location_relation.location.serialize()
            for location_relation in self.location_relations.all().select_related(
                'location'
            )
        ]
