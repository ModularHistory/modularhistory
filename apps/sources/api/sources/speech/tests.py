"""Tests for the source speeches api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.places.factories import PlaceFactory
from apps.propositions.factories import PropositionFactory
from apps.sources.factories import SpeechFactory
from apps.sources.models import Speech
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class SpeechesApiTest(ModerationApiTest):
    """Test the speeches api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'speech'
    api_path_suffix = 'speeches'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.entity_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]
        self.utterances = [PropositionFactory.create(type='speech') for _ in range(3)]
        speech: Speech = SpeechFactory.create(utterance=self.utterances[0])
        speech.attributees.set(shuffled_copy(self.attributee_ids, size=2))
        speech.related_entities.set(shuffled_copy(self.entity_ids, size=2))
        speech.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = speech
        self.verified_container_id = SpeechFactory.create().id

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test speech',
            'type': 'address',
            'audience': 'Test audience',
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
            'utterance': self.utterances[1].id,
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
            'title': 'UPDATED Test speech',
            'type': 'discourse',
            'audience': 'Test audience',
            'date': '2027-01-01 01:01:20',
            'utterance': self.utterances[2].id,
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
