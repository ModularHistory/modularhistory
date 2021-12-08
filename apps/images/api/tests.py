"""Tests for the images api."""

import base64

import pytest

from apps.images.factories import ImageFactory, generate_temporary_image
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class ImagesApiTest(ModerationApiTest):
    """Test the images api."""

    __test__ = True
    api_name = 'images_api'
    api_prefix = 'image'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        image = ImageFactory.create()
        tags = [TopicFactory.create().id for _ in range(4)]
        image.tags.set(shuffled_copy(tags, size=2))
        self.verified_model = image
        self.uncheckable_fields = ['image']

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'image': base64.b64encode(generate_temporary_image().read()).decode('ascii'),
            'description': 'Image 1 Description',
            'caption': 'Image 1 Caption',
            'provider': 'Image 1 Provider',
            'image_type': 'painting',
            'date': '2001-01-01T01:01:20',
            'end_date': '2010-01-01 01:01:25.086200',
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'image': base64.b64encode(generate_temporary_image().read()).decode('ascii'),
            'description': 'UPDATED Image 1 Description',
            'caption': 'UPDATED Image 1 Caption',
            'provider': 'UPDATED Image 1 Provider',
            'date': '2004-01-01T00:00:00',
            'image_type': 'portrait',
            'end_date': '2015-01-01T01:01:25',
        }
