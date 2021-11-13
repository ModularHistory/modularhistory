import os
import shutil
from typing import TYPE_CHECKING

import factory
import pytest
from rest_framework.test import APIClient

if TYPE_CHECKING:
    from pytest import FixtureRequest


@pytest.fixture()
def api_client(request: 'FixtureRequest') -> APIClient:
    """Return an API client to be used in a test."""
    client = APIClient()
    if request.instance:
        request.instance.api_client = client
    return client


@pytest.fixture(autouse=True)
def temporary_media(request: 'FixtureRequest', settings):
    """Create a temporary media directory for testing."""
    id = f'{request.cls.__name__}_{request.node.name}' if request.cls else request.node.name
    settings.MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, '.tmp', id)
    yield settings
    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT)


@pytest.fixture(autouse=True)
def unique_factory():
    """Clean up the faker registry."""
    yield
    for locale, _v in factory.Faker._FAKER_REGISTRY.items():
        factory.Faker._get_faker(locale=locale).unique.clear()
