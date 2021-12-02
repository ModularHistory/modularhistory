"""Tests for the source books api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.sources.factories import BookFactory
from apps.sources.models import Book
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class BooksApiTest(ModerationApiTest):
    """Test the source books api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'book'
    api_path_suffix = 'books'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        book: Book = BookFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        book.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        book.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        book.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = book
        self.verified_container_id = BookFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test book',
            'translator': 'Translator E',
            'publisher': 'Publisher B',
            'edition_year': 2021,
            'edition_number': 3,
            'volume_number': 8,
            'editors': 'Some editor',
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
            'original_publication_date': '0001-01-01T01:01:20.086200Z',
            'original_edition': self.verified_model.id,
            'location': self.location_ids[0],
            'attributees': self.attributee_ids[:2],
            'related_entities': self.entity_ids[:2],
            'tags': self.topic_ids[:2],
            'source_containments': [
                {
                    'container': self.verified_container_id,
                    'page_number': 1,
                    'end_page_number': 100,
                    'phrase': 'reproduced',
                }
            ],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'title': 'UPDATED Test book',
            'translator': 'UPDATED Translator E',
            'publisher': 'UPDATED Publisher B',
            'edition_year': 2024,
            'edition_number': 30,
            'volume_number': 80,
            'editors': 'UPDATED Some editor',
            'date': '2027-01-01 01:01:20',
            'original_publication_date': '0005-01-01T01:01:20.086200Z',
            'original_edition': self.verified_container_id,
            'location': self.location_ids[1],
            'attributees': self.attributee_ids[1:],
            'related_entities': self.entity_ids[1:],
            'tags': self.topic_ids[1:],
            'source_containments': [
                {
                    'container': self.verified_container_id,
                    'page_number': 1,
                    'end_page_number': 100,
                    'phrase': 'cited',
                    'position': 1,
                },
                {
                    'container': self.verified_container_id,
                    'page_number': 200,
                    'end_page_number': 300,
                    'phrase': 'quoted',
                    'position': 2,
                },
            ],
        }
