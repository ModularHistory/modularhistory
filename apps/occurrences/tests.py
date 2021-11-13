"""Tests for the occurrences app."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db()
class TestOccurrences:
    """Test the occurrences app."""

    def test_api_view(self, api_client: APIClient):
        """Test the occurrences API."""
        url = reverse('occurrences_api:occurrence-list')
        response = api_client.get(url)
        assert response.status_code == 200
