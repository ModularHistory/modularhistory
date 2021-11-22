"""Tests for the source reports api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.sources.factories import ReportFactory
from apps.sources.models import Report
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class ReportsApiTest(ModerationApiTest):
    """Test the reports api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'report'
    api_path_suffix = 'reports'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        report: Report = ReportFactory.create()
        report.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        report.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        report.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = report
        self.verified_container_id = ReportFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test report',
            'editors': 'Test editor',
            'publisher': 'Test publisher',
            'number': 10,
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
                    'end_page_number': 2,
                    'phrase': 'archived',
                    'position': 0,
                }
            ],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'title': 'UPDATED Test report',
            'editors': 'UPDATED Test editor',
            'publisher': 'UPDATED Test publisher',
            'number': 20,
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
                    'page_number': 10,
                    'end_page_number': 100,
                    'phrase': 'cited',
                    'position': 3,
                }
            ],
        }
