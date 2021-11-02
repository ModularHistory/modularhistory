"""Tests for the topics api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.topics.factories import TopicFactory
from apps.topics.models import Topic
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def topics_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    topic = TopicFactory.create(verified=True)

    request.cls.verified_topic = topic
    request.cls.relation_fields = ['location']
    request.cls.test_data = {'name': 'Topic 1', 'title': 'Topic 1 Title'}
    request.cls.updated_test_data = {
        'name': 'UPDATED  Topic 1',
        'title': 'UPDATED Topic 1 Title',
    }


@pytest.mark.usefixtures('topics_api_test_data')
class TopicsApiTest(ModerationApiTest):
    """Test the topics api."""

    api_name = 'topics_api'

    verified_topic: Topic

    def test_api_list(self):
        """Test the topics listing API."""
        self.api_view_get_test('topic-list')

    def test_api_detail(self):
        """Test the topics detail API."""
        self.api_view_get_test(
            'topic-detail', url_kwargs={'pk_or_slug': self.verified_topic.id}
        )

    def test_api_create(self):
        """Test the topics creation API."""
        request_params = {'data': self.test_data, 'change_status_code': 201}
        self.api_moderation_change_test(request_params)

    def test_api_update(self):
        """Test the topics update API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_topic.id,
            'view': 'topic-detail',
            'method': 'put',
        }

        self.api_moderation_change_test(request_params)

    def test_api_patch(self):
        """Test the topics patch API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_topic.id,
            'view': 'topic-detail',
            'method': 'patch',
        }

        self.api_moderation_change_test(request_params)

    def test_api_delete(self):
        """Test the topics delete API."""
        request_params = {
            'data': {},
            'view': 'topic-detail',
            'object_id': self.verified_topic.id,
            'method': 'delete',
            'change_status_code': 204,
        }

        (response, change, contribution) = self.api_moderation_view_test(**request_params)

        self.assertIsNotNone(change.changed_object.deleted, 'Deletion change was not created')
