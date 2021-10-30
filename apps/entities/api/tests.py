"""Tests for the entities api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.entities.models import Entity
from apps.images.factories import ImageFactory
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def entities_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    entity = EntityFactory.create(verified=True)

    images = [ImageFactory.create(verified=True).id for _ in range(4)]
    tags = [TopicFactory.create(verified=True).id for _ in range(4)]

    entity.images.set(shuffled_copy(images, size=2))
    entity.tags.set(shuffled_copy(tags, size=2))

    request.cls.verified_entity = entity
    request.cls.uncheckable_fields = ['birth_date', 'death_date']
    request.cls.relation_fields = ['images', 'tags']
    request.cls.test_data = {
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
    request.cls.updated_test_data = {
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


@pytest.mark.usefixtures('entities_api_test_data')
class EntitiesApiTest(ModerationApiTest):
    """Test the entities api."""

    api_name = 'entities_api'

    verified_entity: Entity

    def test_api_list(self):
        """Test the entities listing API."""
        self.api_view_get_test('entity-list')

    def test_api_detail(self):
        """Test the entities detail API."""
        self.api_view_get_test(
            'entity-detail', url_kwargs={'pk_or_slug': self.verified_entity.id}
        )

    def test_api_create(self):
        """Test the entities creation API."""
        request_params = {'data': self.test_data, 'change_status_code': 201}
        self.api_moderation_change_test(request_params)

    def test_api_update(self):
        """Test the entities update API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_entity.id,
            'view': 'entity-detail',
            'method': 'put',
        }

        self.api_moderation_change_test(request_params)

    def test_api_patch(self):
        """Test the entities patch API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_entity.id,
            'view': 'entity-detail',
            'method': 'patch',
        }

        self.api_moderation_change_test(request_params)

    def test_api_delete(self):
        """Test the entities delete API."""
        request_params = {
            'data': {},
            'view': 'entity-detail',
            'object_id': self.verified_entity.id,
            'method': 'delete',
            'change_status_code': 204,
        }

        (response, change, contribution) = self.api_moderation_view_test(**request_params)

        self.assertIsNotNone(change.changed_object.deleted, 'Deletion change was not created')
