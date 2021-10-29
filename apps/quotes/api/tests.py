"""Tests for the quotes app."""

import pytest

from apps.entities.factories import EntityFactory
from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.quotes.factories import QuoteFactory
from apps.quotes.models import Quote
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def quotes_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    quote = QuoteFactory.create(verified=True)

    attributees = [EntityFactory.create(verified=True).id for _ in range(4)]
    images = [ImageFactory.create(verified=True).id for _ in range(4)]
    tags = [TopicFactory.create(verified=True).id for _ in range(4)]

    quote.attributees.set(shuffled_copy(attributees, size=2))
    quote.images.set(shuffled_copy(images, size=2))
    quote.tags.set(shuffled_copy(tags, size=2))

    request.cls.verified_quote = quote
    request.cls.uncheckable_fields = ['date']
    request.cls.relation_fields = ['attributees', 'images', 'tags']
    request.cls.test_data = {
        'title': 'Test Quote TITLE',
        'text': 'Test Quote TEXT',
        'bite': 'Test Quote BITE',
        'date': '2001-01-01 01:01:20.086200',
        'attributees': attributees[:2],
        'images': images[:2],
        'tags': tags[:2],
    }
    request.cls.updated_test_data = {
        'title': 'UPDATED QUOTE TITLE',
        'slug': 'updated-slug',
        'text': 'UPDATED Test Quote TEXT',
        'bite': 'UPDATED Test Quote BITE',
        'date': '2001-01-01 01:01:20.086200',
        'attributees': attributees[1:],
        'images': images[1:],
        'tags': tags[1:],
    }


@pytest.mark.usefixtures('quotes_api_test_data')
class QuotesApiTest(ModerationApiTest):
    """Test the quotes api."""

    api_name = 'quotes_api'

    verified_quote: Quote

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
