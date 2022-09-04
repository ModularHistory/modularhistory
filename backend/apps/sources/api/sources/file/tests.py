"""Tests for the source files api."""
import base64

import pytest

from apps.images.factories import generate_temporary_image
from apps.moderation.api.tests import ModerationApiTest
from apps.sources.factories import SourceFileFactory
from apps.users.factories import UserFactory


class SourceFilesApiTest(ModerationApiTest):
    """Test the source files API."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'sourcefile'
    api_path_suffix = 'files'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.verified_model = SourceFileFactory.create()
        self.uncheckable_fields = ['file']

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'file': base64.b64encode(generate_temporary_image().read()).decode('ascii'),
            'name': 'Some file',
            'first_page_number': 20,
            'page_offset': 10,
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'file': base64.b64encode(generate_temporary_image().read()).decode('ascii'),
            'name': 'UPDATED Some file',
            'first_page_number': 200,
            'page_offset': 100,
        }
