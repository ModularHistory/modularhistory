"""Tests for the source affidavits api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.sources.factories import AffidavitFactory, CollectionFactory
from apps.sources.models import Affidavit
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class AffidavitsApiTest(ModerationApiTest):
    """Test the source affidavits api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'affidavit'
    api_path_suffix = 'affidavits'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        affidavit: Affidavit = AffidavitFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.collection_ids = [CollectionFactory.create().id for _ in range(2)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        affidavit.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        affidavit.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        affidavit.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = affidavit
        self.verified_container_id = AffidavitFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test affidavit',
            'editors': 'Some editor',
            'collection_number': 24,
            'information_url': 'https://modularhistory.orega.org',
            'url': 'https://modularhistory.orega.org',
            'href': 'https://modularhistory.orega.org',
            'location_info': 'Some location info',
            'certifier': 'Some certifier',
            'page_number': 12,
            'end_page_number': 123,
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
            'original_publication_date': '0001-01-01T01:01:20.086200Z',
            'original_edition': self.verified_model.id,
            'related_entities': self.entity_ids[:2],
            'tags': self.topic_ids[:2],
            'attributions': [
                {'attributee': attributee_id, 'position': position}
                for position, attributee_id in enumerate(self.attributee_ids[:2])
            ],
            'location': self.location_ids[0],
            'collection': self.collection_ids[0],
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
            'title': 'UPDATED Test affidavit',
            'editors': 'Some editor',
            'collection_number': 24,
            'information_url': 'https://modularhistory.orega.org',
            'url': 'https://modularhistory.orega.org',
            'href': 'https://modularhistory.orega.org',
            'location_info': 'UPDATED Some location info',
            'certifier': 'UPDATED Some certifier',
            'page_number': 12,
            'end_page_number': 123,
            'date': '2027-01-01 01:01:20',
            'original_publication_date': '0005-01-01T01:01:20.086200Z',
            'original_edition': self.verified_container_id,
            'location': self.location_ids[1],
            'related_entities': self.entity_ids[1:],
            'tags': self.topic_ids[1:],
            'attributions': [
                {'attributee': attributee_id, 'position': position}
                for position, attributee_id in enumerate(self.attributee_ids[1:])
            ],
            'collection': self.collection_ids[1],
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
