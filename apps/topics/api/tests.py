"""Tests for the topics api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class TopicsApiTest(ModerationApiTest):
    """Test the topics api."""

    __test__ = True
    api_name = 'topics_api'
    api_prefix = 'topic'

    @pytest.fixture(autouse=True)
    def topics_api_test_data(self, db):
        self.contributor = UserFactory.create()

        topic = TopicFactory.create(verified=True)

        self.verified_model = topic
        self.relation_fields = ['location']
        self.test_data = {'name': 'Topic 1', 'title': 'Topic 1 Title'}
        self.updated_test_data = {
            'name': 'UPDATED  Topic 1',
            'title': 'UPDATED Topic 1 Title',
        }
