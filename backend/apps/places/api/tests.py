"""Tests for the places api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.places.factories import PlaceFactory
from apps.users.factories import UserFactory


class PlacesApiTest(ModerationApiTest):
    """Test the places API."""

    __test__ = True
    api_name = 'places_api'
    api_prefix = 'place'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.verified_model = PlaceFactory.create()

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        place_continent = PlaceFactory.create(type='places.continent').id
        return {
            'type': 'places.country',
            'name': 'Kigoparene',
            'location': place_continent,
            'preposition': 'at',
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        place_country = PlaceFactory.create(type='places.country').id
        return {
            'type': 'places.city',
            'name': 'Whonix',
            'location': place_country,
            'preposition': 'in',
        }
