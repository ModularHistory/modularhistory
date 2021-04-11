import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestSources:
    """Test the sources app."""

    # @pytest.mark.parametrize('param_name', ['param_value'])
    def test_api_view(self, api_client: APIClient):
        """Test the sources API."""
        url = reverse('sources_api:list')
        response = api_client.get(url)
        assert response.status_code == 200
