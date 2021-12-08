"""Tests for the source interviews api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.sources.factories import InterviewFactory
from apps.sources.models import Interview
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class InterviewsApiTest(ModerationApiTest):
    """Test the interviews api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'interview'
    api_path_suffix = 'interviews'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        interview: Interview = InterviewFactory.create()
        interview.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        interview.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        interview.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = interview
        self.verified_container_id = InterviewFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test interview',
            'interviewers': 'Interviewer 1, Interviewer A',
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
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
            'title': 'UPDATED Test interview',
            'interviewers': 'Interviewer 2, Interviewer B',
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
