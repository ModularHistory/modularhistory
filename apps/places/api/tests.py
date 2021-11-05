"""Tests for the places api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.places.factories import PlaceFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def places_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    place = PlaceFactory.create(verified=True)
    place_continent = PlaceFactory.create(verified=True, type='places.continent').id
    place_country = PlaceFactory.create(verified=True, type='places.country').id

    request.cls.verified_model = place
    request.cls.relation_fields = ['location']
    request.cls.test_data = {
        'type': 'places.country',
        'name': 'Kigoparene',
        'location': place_continent,
        'preposition': 'at',
    }
    request.cls.updated_test_data = {
        'type': 'places.city',
        'name': 'Whonix',
        'location': place_country,
        'preposition': 'in',
    }


@pytest.mark.usefixtures('places_api_test_data')
class PlacesApiTest(ModerationApiTest):
    """Test the places api."""

    __test__ = True
    api_name = 'places_api'
    api_prefix = 'place'
