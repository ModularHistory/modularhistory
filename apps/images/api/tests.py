"""Tests for the images api."""

import pytest

from apps.images.factories import ImageFactory, fake_image
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


@pytest.fixture(scope='class')
def images_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    image = ImageFactory.create(verified=True)

    tags = [TopicFactory.create(verified=True).id for _ in range(4)]

    image.tags.set(shuffled_copy(tags, size=2))

    request.cls.verified_model = image
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

    __test__ = True
    api_name = 'images_api'
    api_prefix = 'image'
