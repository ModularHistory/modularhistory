"""Tests for the entities api."""

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.entities.factories import EntityFactory
from apps.entities.models import Entity
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
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.content_type = ContentType.objects.get_for_model(Entity)
        entity: Entity = EntityFactory.create()
        self.images = [ImageFactory.create().id for _ in range(4)]
        self.tags = [TopicFactory.create().id for _ in range(4)]
        entity.images.set(shuffled_copy(self.images, size=2))
        entity.tags.set(shuffled_copy(self.tags, size=2))
        self.verified_model = entity
        self.uncheckable_fields = ['birth_date', 'death_date']
        self.relation_fields = ['images', 'tags']

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        """Data for creating an entity."""
        return {
            'type': 'entities.person',
            'name': 'Test Entity John Doe 1',
            'unabbreviated_name': 'John Doe 1',
            'description': '<p>Test Entity description </p>',
            'aliases': ['Jane Doe', 'John The Baptist'],
            'birth_date': '0001-01-01 01:01:20.086200',
            'death_date': '2066-06-06 05:03:02',
            'images': self.images[:2],
            'tags': self.tags[:2],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        """Data for updating an entity."""
        return {
            'type': 'entities.person',
            'name': 'UPDATED Test Entity John Doe 1',
            'unabbreviated_name': 'UPDATED John Doe 1',
            'description': '<p>UPDATED Test Entity description </p>',
            'aliases': ['UPDATED Jane Doe', 'UPDATED John The Baptist'],
            'birth_date': '0001-01-01 01:01:20.086200',
            'death_date': '2066-06-06 05:03:02',
            'images': self.images[1:],
            'tags': self.tags[1:],
        }
