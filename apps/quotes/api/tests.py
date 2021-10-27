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
def quote_class(request):

    request.cls.contributor = UserFactory.create()
    request.cls.verified_quote = QuoteFactory.create(verified=True)


@pytest.mark.usefixtures('quote_class')
class TestQuotesApi(APITestCase):
    """Test the quotes api."""

    api_name = 'quotes_api'

    api_client = APIClient()

    contributor: User
    verified_quote: Quote

    def api_view_get_test(self, view, url_kwargs=None, status_code=200):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        response = self.api_client.get(path)
        assert response.status_code == status_code

    def api_create_view_test(self, data, view='api-root', url_kwargs=None):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)

        self.assertEqual(
            self.api_client.post(path, data).status_code,
            401,
            'Deny creation without authentication',
        )

        self.api_client.force_authenticate(self.contributor)
        response = self.api_client.post(path, data)
        self.api_client.logout()

        self.assertEqual(response.status_code, 201, 'Object creation successful')

        created_change = Change.objects.get(
            initiator=self.contributor, object_id=response.data.get('id')
        )

        contributions = ContentContribution.objects.filter(
            contributor=self.contributor, change_id=created_change
        )

        # currently fails, but it shouldn't..
        assert contributions.count() == 0

        # currently doesn't fail, it should..
        assert contributions[0].content_before == contributions[1].content_before

        return response.data

    def test_api_list(self):
        """Test the quotes API listing."""
        self.api_view_get_test('quote-list')

    def test_api_detail(self):
        self.api_view_get_test(
            'quote-detail', url_kwargs={'pk_or_slug': self.verified_quote.id}
        )

    def test_api_create(self):
        quote_data = {
            'title': 'Test Quote TITLE',
            'text': 'Test Quote TEXT',
            'date': '2001-01-01 01:01:20.086200',
        }
        entity_data = {
            'type': 'entities.person',
            'name': 'Test Entity John Doe 1100',
            'unabbreviatedName': 'John Doe 1100',
            'description': '<p>Test Entity description </p>',
            'aliases': ['Jane Doe', 'John The Baptist'],
            'birthDate': '0001-01-01 01:01:20.086200',
            'deathDate': '2066-06-06 05:03:02',
        }
        self.api_create_view_test(data=quote_data)
