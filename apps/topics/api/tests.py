"""Tests for the topics api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def topics_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    topic = TopicFactory.create(verified=True)

    request.cls.verified_model = topic
    request.cls.relation_fields = ['location']
    request.cls.test_data = {'name': 'Topic 1', 'title': 'Topic 1 Title'}
    request.cls.updated_test_data = {
        'name': 'UPDATED  Topic 1',
        'title': 'UPDATED Topic 1 Title',
    }


@pytest.mark.usefixtures('topics_api_test_data')
class TopicsApiTest(ModerationApiTest):
    """Test the topics api."""

    __test__ = True
    api_name = 'topics_api'
    api_prefix = 'topic'
