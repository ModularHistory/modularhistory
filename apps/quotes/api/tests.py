"""Tests for the quotes app."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apps.moderation.models import Change, ContentContribution
from apps.quotes.factories import QuoteFactory
from apps.quotes.models import Quote
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture(scope='class')
def quote_api_test_data(request):
    request.cls.contributor = UserFactory.create()
    request.cls.verified_quote = QuoteFactory.create(verified=True)

    request.cls.uncheckable_fields = ['date']
    request.cls.test_data = {
        'title': 'Test Quote TITLE',
        'text': 'Test Quote TEXT',
        'date': '2001-01-01 01:01:20.086200',
    }
    request.cls.updated_test_data = {
        'title': 'UPDATED QUOTE TITLE',
        'slug': 'updated-slug',
        'text': 'UPDATED Test Quote TEXT',
        'bite': 'UPDATED Test Quote BITE',
        'date': '2001-01-01 01:01:20.086200',
    }


@pytest.mark.usefixtures('quote_api_test_data')
class QuotesApiTest(APITestCase):
    """Test the quotes api."""

    api_client = APIClient()
    api_name = 'quotes_api'

    contributor: User

    uncheckable_fields: list
    test_data: dict
    updated_test_data: dict

    verified_quote: Quote

    def api_view_get_test(self, view, url_kwargs=None, status_code=200):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        response = self.api_client.get(path)
        assert response.status_code == status_code

    def api_moderation_view_test(
        self,
        data,
        view='api-root',
        url_kwargs=None,
        change_status_code=200,
        method='post',
        object_id=None,
    ):
        if url_kwargs is None:
            url_kwargs = {}
        if object_id:
            url_kwargs.update({'pk_or_slug': object_id})
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)

        self.assertEqual(
            self.api_client.post(path, data).status_code,
            401,
            'Deny creation without authentication',
        )

        self.api_client.force_authenticate(self.contributor)

        api_request = getattr(self.api_client, method)
        response = api_request(path, data)

        self.api_client.logout()

        self.assertEqual(
            response.status_code, change_status_code, 'Change status code is not correct'
        )

        if response.data and 'id' in response.data:
            object_id = response.data.get('id')

        created_change = Change.objects.get(
            initiator=self.contributor,
            object_id=object_id,
        )

        contributions = ContentContribution.objects.filter(
            contributor=self.contributor, change_id=created_change
        )

        # TODO: find out why multiple contributions are created
        self.assertGreater(
            contributions.count(),
            0,
            'Incorrect count of Contributions were created for a change',
        )

        return response.data, created_change, contributions

    def api_moderation_change_test(self, request_params):
        (response, change, contribution) = self.api_moderation_view_test(**request_params)
        for key, value in request_params.get('data').items():
            if key not in self.uncheckable_fields:
                self.assertEqual(
                    getattr(change.changed_object, key),
                    value,
                    f'{key} field was not updated correctly',
                )

    def test_api_list(self):
        """Test the quotes listing API."""
        self.api_view_get_test('quote-list')

    def test_api_detail(self):
        """Test the quotes detail API."""
        self.api_view_get_test(
            'quote-detail', url_kwargs={'pk_or_slug': self.verified_quote.id}
        )

    def test_api_create(self):
        """Test the quotes creation API."""
        request_params = {'data': self.test_data, 'change_status_code': 201}
        self.api_moderation_change_test(request_params)

    def test_api_update(self):
        """Test the quotes update API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_quote.id,
            'view': 'quote-detail',
            'method': 'put',
        }

        self.api_moderation_change_test(request_params)

    def test_api_patch(self):
        """Test the quotes patch API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_quote.id,
            'view': 'quote-detail',
            'method': 'patch',
        }

        self.api_moderation_change_test(request_params)

    def test_api_delete(self):
        """Test the quotes delete API."""
        request_params = {
            'data': {},
            'view': 'quote-detail',
            'object_id': self.verified_quote.id,
            'method': 'delete',
            'change_status_code': 204,
        }

        (response, change, contribution) = self.api_moderation_view_test(**request_params)

        self.assertIsNotNone(change.changed_object.deleted, 'Deletion change was not created')
