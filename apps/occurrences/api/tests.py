"""Tests for the occurrences api."""

import pytest

from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.occurrences.factories import OccurrenceFactory
from apps.occurrences.models import Occurrence
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def occurrences_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    occurrence = OccurrenceFactory.create(verified=True)

    images = [ImageFactory.create(verified=True).id for _ in range(4)]
    tags = [TopicFactory.create(verified=True).id for _ in range(4)]

    occurrence.images.set(shuffled_copy(images, size=2))
    occurrence.tags.set(shuffled_copy(tags, size=2))

    request.cls.verified_occurrence = occurrence
    request.cls.uncheckable_fields = ['date']
    request.cls.relation_fields = ['images', 'tags']
    request.cls.test_data = {
        'type': 'propositions.occurrence',
        'title': 'Some title',
        'slug': 'some-slug',
        'summary': 'Some summary',
        'elaboration': 'Some elaboration',
        'certainty': 2,
        'date': '0001-01-01T01:01:20.056200Z',
        'postscript': 'Some postscript',
        'images': images[:2],
        'tags': tags[:2],
    }
    request.cls.updated_test_data = {
        'type': 'propositions.occurrence',
        'title': 'UPDATED Some title',
        'slug': 'UPDATED some-slug',
        'summary': 'UPDATED Some summary',
        'elaboration': 'UPDATED Some elaboration',
        'postscript': 'UPDATED Some postscript',
        'certainty': 2,
        'date': '0001-01-01T01:01:20.056200Z',
        'images': images[1:],
        'tags': tags[1:],
    }


@pytest.mark.usefixtures('occurrences_api_test_data')
class OccurrencesApiTest(ModerationApiTest):
    """Test the occurrences api."""

    api_name = 'occurrences_api'

    verified_occurrence: Occurrence

    def test_api_list(self):
        """Test the occurrences listing API."""
        self.api_view_get_test('occurrence-list')

    def test_api_detail(self):
        """Test the occurrences detail API."""
        self.api_view_get_test(
            'occurrence-detail', url_kwargs={'pk_or_slug': self.verified_occurrence.id}
        )

    def test_api_create(self):
        """Test the occurrences creation API."""
        request_params = {'data': self.test_data, 'change_status_code': 201}
        self.api_moderation_change_test(request_params)

    def test_api_update(self):
        """Test the occurrences update API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_occurrence.id,
            'view': 'occurrence-detail',
            'method': 'put',
        }

        self.api_moderation_change_test(request_params)

    def test_api_patch(self):
        """Test the occurrences patch API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_occurrence.id,
            'view': 'occurrence-detail',
            'method': 'patch',
        }

        self.api_moderation_change_test(request_params)

    def test_api_delete(self):
        """Test the occurrences delete API."""
        request_params = {
            'data': {},
            'view': 'occurrence-detail',
            'object_id': self.verified_occurrence.id,
            'method': 'delete',
            'change_status_code': 204,
        }

        (response, change, contribution) = self.api_moderation_view_test(**request_params)

        self.assertIsNotNone(change.changed_object.deleted, 'Deletion change was not created')
