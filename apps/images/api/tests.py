"""Tests for the images api."""

import pytest

from apps.images.factories import ImageFactory, fake_image
from apps.images.models import Image
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def images_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    image = ImageFactory.create(verified=True)

    tags = [TopicFactory.create(verified=True).id for _ in range(4)]

    image.tags.set(shuffled_copy(tags, size=2))

    request.cls.verified_image = image
    request.cls.uncheckable_fields = ['date', 'end_date', 'image']
    request.cls.test_data = {
        'image': fake_image(),
        'description': 'Image 1 Description',
        'caption': 'Image 1 Caption',
        'provider': 'Image 1 Provider',
        'date': '2001-01-01T01:01:20',
    }
    request.cls.updated_test_data = {
        'image': fake_image(),
        'description': 'UPDATED Image 1 Description',
        'caption': 'UPDATED Image 1 Caption',
        'provider': 'UPDATED Image 1 Provider',
        'date': '2004-01-01T00:00:00',
        'end_date': '2015-01-01T01:01:25',
    }


@pytest.mark.usefixtures('images_api_test_data')
class ImagesApiTest(ModerationApiTest):
    """Test the images api."""

    api_name = 'images_api'

    verified_image: Image

    def test_api_list(self):
        """Test the images listing API."""
        self.api_view_get_test('image-list')

    def test_api_detail(self):
        """Test the images detail API."""
        self.api_view_get_test(
            'image-detail', url_kwargs={'pk_or_slug': self.verified_image.id}
        )

    def test_api_create(self):
        """Test the images creation API."""
        request_params = {
            'data': self.test_data,
            'format': 'multipart',
            'change_status_code': 201,
        }
        self.api_moderation_change_test(request_params)

    def test_api_update(self):
        """Test the images update API."""
        request_params = {
            'data': self.updated_test_data,
            'format': 'multipart',
            'object_id': self.verified_image.id,
            'view': 'image-detail',
            'method': 'put',
        }

        self.api_moderation_change_test(request_params)

    def test_api_patch(self):
        """Test the images patch API."""
        request_params = {
            'data': self.updated_test_data,
            'format': 'multipart',
            'object_id': self.verified_image.id,
            'view': 'image-detail',
            'method': 'patch',
        }

        self.api_moderation_change_test(request_params)

    def test_api_delete(self):
        """Test the images delete API."""
        request_params = {
            'data': {},
            'view': 'image-detail',
            'object_id': self.verified_image.id,
            'method': 'delete',
            'change_status_code': 204,
        }

        (response, change, contribution) = self.api_moderation_view_test(**request_params)

        self.assertIsNotNone(change.changed_object.deleted, 'Deletion change was not created')
