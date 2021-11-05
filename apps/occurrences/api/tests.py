"""Tests for the occurrences api."""

import pytest

from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.occurrences.factories import OccurrenceFactory
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

    request.cls.verified_model = occurrence
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

    __test__ = True
    api_name = 'occurrences_api'
    api_prefix = 'occurrence'
