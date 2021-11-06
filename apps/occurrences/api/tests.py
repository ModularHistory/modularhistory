"""Tests for the occurrences api."""

from typing import TYPE_CHECKING

import pytest

from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.occurrences.factories import OccurrenceFactory
from apps.occurrences.models import Occurrence
from apps.topics.factories import TopicFactory
from apps.topics.models import Topic
from apps.users.factories import UserFactory

if TYPE_CHECKING:
    from apps.users.models import User


class OccurrencesApiTest(ModerationApiTest):
    """Test the occurrences api."""

    __test__ = True
    api_name = 'occurrences_api'
    api_prefix = 'occurrence'

    @pytest.fixture(autouse=True, scope='function')
    def data(self, db):
        self.contributor: 'User' = UserFactory.create()
        occurrence: 'Occurrence' = OccurrenceFactory.create(verified=True)
        image_ids: list[int] = [ImageFactory.create(verified=True).id for _ in range(4)]
        topic_ids: list[int] = [TopicFactory.create(verified=True).id for _ in range(4)]
        for topic_id in topic_ids:
            assert Topic.objects.filter(id=topic_id).exists()
        occurrence.images.set(shuffled_copy(image_ids, size=2))
        occurrence.tags.set(shuffled_copy(topic_ids, size=2))
        self.verified_model = occurrence
        self.uncheckable_fields = ['date']
        self.relation_fields = ['images', 'tags']
        self.test_data = {
            'type': 'propositions.occurrence',
            'title': 'Some title',
            'slug': 'some-slug',
            'summary': 'Some summary',
            'elaboration': 'Some elaboration',
            'certainty': 2,
            'date': '0001-01-01T01:01:20.056200Z',
            'postscript': 'Some postscript',
            'images': image_ids[:2],
            'tags': topic_ids[:2],
        }
        self.updated_test_data = {
            'type': 'propositions.occurrence',
            'title': 'UPDATED Some title',
            'slug': 'UPDATED some-slug',
            'summary': 'UPDATED Some summary',
            'elaboration': 'UPDATED Some elaboration',
            'postscript': 'UPDATED Some postscript',
            'certainty': 2,
            'date': '0001-01-01T01:01:20.056200Z',
            'images': image_ids[1:],
            'tags': topic_ids[1:],
        }
