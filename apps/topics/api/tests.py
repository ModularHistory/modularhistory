"""Tests for the topics api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.topics.factories import TopicFactory
from apps.topics.models import Topic
from apps.users.factories import UserFactory


class TopicsApiTest(ModerationApiTest):
    """Test the topics api."""

    __test__ = True
    api_name = 'topics_api'
    api_prefix = 'topic'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        topic: Topic = TopicFactory.create()
        self.verified_model = topic

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {'name': 'Topic 1', 'title': 'Topic 1 Title'}

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'name': 'UPDATED  Topic 1',
            'title': 'UPDATED Topic 1 Title',
        }
