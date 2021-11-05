"""Tests for the quotes api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.quotes.factories import QuoteFactory
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

    request.cls.verified_model = quote
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

    __test__ = True
    api_name = 'quotes_api'
    api_prefix = 'quote'
