"""Tests for the source webpages api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.sources.factories import PublicationFactory, WebpageFactory, WebsiteFactory
from apps.sources.models import Webpage
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class PublicationsApiTest(ModerationApiTest):
    """Test the source publications API."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'publication'
    api_path_suffix = 'publications'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.verified_model = PublicationFactory.create()

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'name': 'Some publication',
            'type': 'sources.journal',
            'aliases': 'Some aliases',
            'description': 'Some description',
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'name': 'UPDATED Some publication',
            'type': 'sources.magazine',
            'aliases': 'UPDATED Some aliases',
            'description': 'UPDATED Some description',
        }


class WebsitesApiTest(ModerationApiTest):
    """Test the source websites API."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'website'
    api_path_suffix = 'websites'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.verified_model = WebsiteFactory.create()

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'name': 'Some website',
            'aliases': 'Some aliases',
            'description': 'Some description',
            'owner': 'Some owner',
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'name': 'UPDATED Some website',
            'aliases': 'UPDATED Some aliases',
            'description': 'UPDATED Some description',
            'owner': 'UPDATED Some owner',
        }


class WebpagesApiTest(ModerationApiTest):
    """Test the webpages api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'webpage'
    api_path_suffix = 'webpages'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        self.website_ids = [WebsiteFactory.create().id for _ in range(2)]
        webpage: Webpage = WebpageFactory.create()
        webpage.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        webpage.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        webpage.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = webpage
        self.verified_container_id = WebpageFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test webpage',
            'editors': 'Test editor',
            # 'website_name': 'Test website',
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
            'original_publication_date': '0001-01-01T01:01:20.086200Z',
            'original_edition': self.verified_model.id,
            'location': self.location_ids[0],
            'website': self.website_ids[0],
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
            'title': 'UPDATED Test webpage',
            'editors': 'UPDATED Test editor',
            # 'website_name': 'UPDATED Test website',
            'date': '2027-01-01 01:01:20',
            'original_publication_date': '0005-01-01T01:01:20.086200Z',
            'original_edition': self.verified_container_id,
            'location': self.location_ids[1],
            'website': self.website_ids[1],
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
