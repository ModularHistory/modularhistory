"""Tests for the images api."""

import pytest

from apps.images.factories import ImageFactory, fake_image
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class ImagesApiTest(ModerationApiTest):
    """Test the images api."""

    __test__ = True
    api_name = 'images_api'
    api_prefix = 'image'

    @pytest.fixture(autouse=True)
    def images_api_test_data(self, db):
        self.contributor = UserFactory.create()
        image = ImageFactory.create(verified=True)
        tags = [TopicFactory.create(verified=True).id for _ in range(4)]
        image.tags.set(shuffled_copy(tags, size=2))
        self.verified_model = image
        self.uncheckable_fields = ['date', 'end_date', 'image']
        self.test_data = {
            'image': fake_image(),
            'description': 'Image 1 Description',
            'caption': 'Image 1 Caption',
            'provider': 'Image 1 Provider',
            'date': '2001-01-01T01:01:20',
        }
        self.updated_test_data = {
            'image': fake_image(),
            'description': 'UPDATED Image 1 Description',
            'caption': 'UPDATED Image 1 Caption',
            'provider': 'UPDATED Image 1 Provider',
            'date': '2004-01-01T00:00:00',
            'end_date': '2015-01-01T01:01:25',
        }
