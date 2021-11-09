"""Tests for the images api."""

import base64

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.images.factories import ImageFactory, generate_temporary_image
from apps.images.models import Image
from apps.moderation.api.tests import ModerationApiTest, shuffled_copy
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class ImagesApiTest(ModerationApiTest):
    """Test the images api."""

    __test__ = True
    api_name = 'images_api'
    api_prefix = 'image'
    extra_api_request_kwargs = {'content_type': 'multipart/form-data'}  # TODO

    @pytest.fixture(autouse=True)
    def data(self, db):
        self.contributor = UserFactory.create()
        self.content_type = ContentType.objects.get_for_model(Image)
        image = ImageFactory.create(verified=True)
        tags = [TopicFactory.create(verified=True).id for _ in range(4)]
        image.tags.set(shuffled_copy(tags, size=2))
        self.verified_model = image
        self.uncheckable_fields = ['date', 'end_date', 'image']

    @pytest.fixture()
    def data_for_creation(self, db, data):
        return {
            'image': base64.b64encode(generate_temporary_image().read()).decode('ascii'),
            'description': 'Image 1 Description',
            'caption': 'Image 1 Caption',
            'provider': 'Image 1 Provider',
            'date': '2001-01-01T01:01:20',
        }

    @pytest.fixture()
    def data_for_update(self, db, data):
        return {
            'image': base64.b64encode(generate_temporary_image().read()).decode('ascii'),
            'description': 'UPDATED Image 1 Description',
            'caption': 'UPDATED Image 1 Caption',
            'provider': 'UPDATED Image 1 Provider',
            'date': '2004-01-01T00:00:00',
            'end_date': '2015-01-01T01:01:25',
        }
