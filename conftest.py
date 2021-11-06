from typing import TYPE_CHECKING

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
