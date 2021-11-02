"""Tests for the places api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.places.factories import PlaceFactory
from apps.places.models import Place
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def places_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    place = PlaceFactory.create(verified=True)
    place_continent = PlaceFactory.create(verified=True, type='places.continent').id
    place_country = PlaceFactory.create(verified=True, type='places.country').id

    request.cls.verified_place = place
    request.cls.uncheckable_fields = ['date']
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

    api_name = 'places_api'

    verified_place: Place

    def test_api_list(self):
        """Test the places listing API."""
        self.api_view_get_test('place-list')

    def test_api_detail(self):
        """Test the places detail API."""
        self.api_view_get_test(
            'place-detail', url_kwargs={'pk_or_slug': self.verified_place.id}
        )

    def test_api_create(self):
        """Test the places creation API."""
        request_params = {'data': self.test_data, 'change_status_code': 201}
        self.api_moderation_change_test(request_params)

    def test_api_update(self):
        """Test the places update API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_place.id,
            'view': 'place-detail',
            'method': 'put',
        }

        self.api_moderation_change_test(request_params)

    def test_api_patch(self):
        """Test the places patch API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_place.id,
            'view': 'place-detail',
            'method': 'patch',
        }

        self.api_moderation_change_test(request_params)

    def test_api_delete(self):
        """Test the places delete API."""
        request_params = {
            'data': {},
            'view': 'place-detail',
            'object_id': self.verified_place.id,
            'method': 'delete',
            'change_status_code': 204,
        }

        (response, change, contribution) = self.api_moderation_view_test(**request_params)

        self.assertIsNotNone(change.changed_object.deleted, 'Deletion change was not created')
