"""Tests for the occurrences api."""

from typing import TYPE_CHECKING

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.occurrences.factories import OccurrenceFactory
from apps.propositions.models import Proposition
from apps.topics.factories import TopicFactory
from apps.topics.models import Topic
from apps.users.factories import UserFactory

if TYPE_CHECKING:
    from apps.propositions.models import Occurrence
    from apps.users.models import User


class OccurrencesApiTest(ModerationApiTest):
    """Test the occurrences api."""

    __test__ = True
    api_name = 'occurrences_api'
    api_prefix = 'occurrence'

    @pytest.fixture(autouse=True, scope='function')
    def data(self, db: None):
        self.contributor: 'User' = UserFactory.create()
        self.content_type = ContentType.objects.get_for_model(Proposition)
        occurrence: 'Occurrence' = OccurrenceFactory.create(verified=True)
        self.image_ids: list[int] = [ImageFactory.create(verified=True).id for _ in range(4)]
        self.topic_ids: list[int] = [TopicFactory.create(verified=True).id for _ in range(4)]
        for topic_id in self.topic_ids:
            assert Topic.objects.filter(id=topic_id).exists()
        occurrence.images.set(shuffled_copy(self.image_ids, size=2))
        occurrence.tags.set(shuffled_copy(self.topic_ids, size=2))
        self.verified_model = occurrence
        self.uncheckable_fields = ['date']
        self.relation_fields = ['images', 'tags']

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'type': 'propositions.occurrence',
            'title': 'Some title',
            'slug': 'some-slug',
            'summary': 'Some summary',
            'elaboration': 'Some elaboration',
            'certainty': 2,
            'date': '0001-01-01T01:01:20.056200Z',
            'postscript': 'Some postscript',
            'images': self.image_ids[:2],
            'tags': self.topic_ids[:2],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'type': 'propositions.occurrence',
            'title': 'UPDATED Some title',
            'slug': 'UPDATED some-slug',
            'summary': 'UPDATED Some summary',
            'elaboration': 'UPDATED Some elaboration',
            'postscript': 'UPDATED Some postscript',
            'certainty': 2,
            'date': '0001-01-01T01:01:20.056200Z',
            'images': self.image_ids[1:],
            'tags': self.topic_ids[1:],
        }