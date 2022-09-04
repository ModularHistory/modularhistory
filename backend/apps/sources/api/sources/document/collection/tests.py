"""Tests for the source document repositories/collections api."""

import pytest

from apps.moderation.api.tests import ModerationApiTest
from apps.places.factories import PlaceFactory
from apps.sources.factories import CollectionFactory, RepositoryFactory
from apps.users.factories import UserFactory


class RepositoriesApiTest(ModerationApiTest):
    """Test the source document repositories API."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'repository'
    api_path_suffix = 'repositories'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.verified_model = RepositoryFactory.create()
        self.location_ids = [PlaceFactory.create().id for _ in range(2)]

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'name': 'Some repository',
            'owner': 'Some owner',
            'location': self.location_ids[0],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'name': 'UPDATED Some repository',
            'owner': 'UPDATED Some owner',
            'location': self.location_ids[1],
        }


class CollectionsApiTest(ModerationApiTest):
    """Test the collections API."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'collection'
    api_path_suffix = 'collections'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.verified_model = CollectionFactory.create()
        self.repo_ids = [RepositoryFactory.create().id for _ in range(2)]

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'name': 'Some collection',
            'url': 'https://some.url',
            'repository': self.repo_ids[0],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'name': 'UPDATED Some collection',
            'url': 'https://some.updated.url',
            'repository': self.repo_ids[1],
        }
