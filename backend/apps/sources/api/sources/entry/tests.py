"""Tests for the source entries api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.sources.factories import EntryFactory
from apps.sources.models import Entry
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class EntriesApiTest(ModerationApiTest):
    """Test the entries api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'entry'
    api_path_suffix = 'entries'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        entry: Entry = EntryFactory.create()
        entry.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        entry.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        entry.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = entry
        self.verified_container_id = EntryFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test entry',
            'page_number': 23,
            'end_page_number': 1,
            'editors': 'Some editor',
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
            'original_publication_date': '0001-01-01T01:01:20.086200Z',
            'original_edition': self.verified_model.id,
            'location': self.location_ids[0],
            'related_entities': self.entity_ids[:2],
            'tags': self.topic_ids[:2],
            'attributions': [
                {'attributee': attributee_id, 'position': position}
                for position, attributee_id in enumerate(self.attributee_ids[:2])
            ],
            'source_containments': [
                {
                    'container': self.verified_container_id,
                    'page_number': 1,
                    'end_page_number': 2,
                    'phrase': 'archived',
                    'position': 0,
                }
            ],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'title': 'UPDATED Test entry',
            'page_number': 25,
            'end_page_number': 12,
            'editors': 'UPDATED Some editor',
            'original_edition': self.verified_container_id,
            'original_publication_date': '0005-01-01T01:01:20.086200Z',
            'date': '2027-01-01 01:01:20',
            'location': self.location_ids[1],
            'related_entities': self.entity_ids[1:],
            'tags': self.topic_ids[1:],
            'attributions': [
                {'attributee': attributee_id, 'position': position}
                for position, attributee_id in enumerate(self.attributee_ids[1:])
            ],
            'source_containments': [
                {
                    'container': self.verified_container_id,
                    'page_number': 10,
                    'end_page_number': 100,
                    'phrase': 'cited',
                    'position': 3,
                }
            ],
        }
