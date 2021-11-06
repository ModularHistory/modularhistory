import pytest
from pytest import FixtureRequest
from rest_framework.test import APIClient


@pytest.fixture()
def api_client(request: FixtureRequest) -> APIClient:
    """Return an API client to be used in a test."""
    client = APIClient()
    if request.instance:
        request.instance.api_client = client
    return client
