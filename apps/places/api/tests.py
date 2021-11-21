"""Tests for the places api."""

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.moderation.api.tests import ModerationApiTest
from apps.places.factories import PlaceFactory
from apps.places.models import Place
from apps.users.factories import UserFactory


class PlacesApiTest(ModerationApiTest):
    """Test the places API."""

    __test__ = True
    api_name = 'places_api'
    api_prefix = 'place'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.content_type = ContentType.objects.get_for_model(Place)
        self.verified_model = PlaceFactory.create(verified=True)

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        place_continent = PlaceFactory.create(verified=True, type='places.continent').id
        return {
            'type': 'places.country',
            'name': 'Kigoparene',
            'location': place_continent,
            'preposition': 'at',
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        place_country = PlaceFactory.create(verified=True, type='places.country').id
        return {
            'type': 'places.city',
            'name': 'Whonix',
            'location': place_country,
            'preposition': 'in',
        }
