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
    def places_api_test_data(self, db):
        self.contributor = UserFactory.create()
        place = PlaceFactory.create(verified=True)
        place_continent = PlaceFactory.create(verified=True, type='places.continent').id
        place_country = PlaceFactory.create(verified=True, type='places.country').id
        self.verified_model = place
        self.relation_fields = ['location']
        self.test_data = {
            'type': 'places.country',
            'name': 'Kigoparene',
            'location': place_continent,
            'preposition': 'at',
        }
        self.updated_test_data = {
            'type': 'places.city',
            'name': 'Whonix',
            'location': place_country,
            'preposition': 'in',
        }
