"""Tests for the entities api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class EntitiesApiTest(ModerationApiTest):
    """Test the entities api."""

    __test__ = True
    api_name = 'entities_api'
    api_prefix = 'entity'

    @pytest.fixture(autouse=True)
    def data(self, db):
        self.contributor = UserFactory.create()
        entity = EntityFactory.create(verified=True)
        images = [ImageFactory.create(verified=True).id for _ in range(4)]
        tags = [TopicFactory.create(verified=True).id for _ in range(4)]
        entity.images.set(shuffled_copy(images, size=2))
        entity.tags.set(shuffled_copy(tags, size=2))
        self.verified_model = entity
        self.uncheckable_fields = ['birth_date', 'death_date']
        self.relation_fields = ['images', 'tags']
        self.test_data = {
            'type': 'entities.person',
            'name': 'Test Entity John Doe 1',
            'unabbreviated_name': 'John Doe 1',
            'description': '<p>Test Entity description </p>',
            'aliases': ['Jane Doe', 'John The Baptist'],
            'birth_date': '0001-01-01 01:01:20.086200',
            'death_date': '2066-06-06 05:03:02',
            'images': images[:2],
            'tags': tags[:2],
        }
        self.updated_test_data = {
            'type': 'entities.person',
            'name': 'UPDATED Test Entity John Doe 1',
            'unabbreviated_name': 'UPDATED John Doe 1',
            'description': '<p>UPDATED Test Entity description </p>',
            'aliases': ['UPDATED Jane Doe', 'UPDATED ohn The Baptist'],
            'birth_date': '0001-01-01 01:01:20.086200',
            'death_date': '2066-06-06 05:03:02',
            'images': images[1:],
            'tags': tags[1:],
        }
