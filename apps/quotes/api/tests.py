"""Tests for the quotes api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.quotes.factories import QuoteFactory
from apps.quotes.models import Quote
from apps.sources.factories import ArticleFactory
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class QuotesApiTest(ModerationApiTest):
    """Test the quotes api."""

    __test__ = True
    api_name = 'quotes_api'
    api_prefix = 'quote'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        quote: Quote = QuoteFactory.create()
        self.attributees = [EntityFactory.create().id for _ in range(4)]
        self.images = [ImageFactory.create().id for _ in range(4)]
        self.tags = [TopicFactory.create().id for _ in range(4)]
        self.article_ids = [ArticleFactory.create().id for _ in range(2)]
        quote.attributees.set(shuffled_copy(self.attributees, size=2))
        quote.images.set(shuffled_copy(self.images, size=2))
        quote.tags.set(shuffled_copy(self.tags, size=2))
        self.verified_model = quote

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test Quote TITLE',
            'text': 'Test Quote TEXT',
            'bite': 'Test Quote BITE',
            'date': '2001-01-01 01:01:20.086200',
            'attributees': self.attributees[:2],
            'images': self.images[:2],
            'tags': self.tags[:2],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'title': 'UPDATED QUOTE TITLE',
            'slug': 'updated-slug',
            'text': 'UPDATED Test Quote TEXT',
            'bite': 'UPDATED Test Quote BITE',
            'date': '2001-01-01 01:01:20.086200',
            'attributees': self.attributees[1:],
            'images': self.images[1:],
            'tags': self.tags[1:],
            'citations': [
                {
                    'content_object': self.verified_model.id,
                    'source': self.article_ids[0],
                    'citation_phrase': 'quoted in',
                    'position': 0,
                },
                {
                    'content_object': self.verified_model.id,
                    'source': self.article_ids[1],
                    'citation_phrase': 'partially reproduced in',
                    'position': 1,
                },
            ],
        }
