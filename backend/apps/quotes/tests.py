"""Tests for the quotes app."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db()
class TestQuotes:
    """Test the quotes app."""

    def test_api_view(self, api_client: APIClient):
        """Test the quotes API."""
        url = reverse('quotes_api:quote-list')
        response = api_client.get(url)
        assert response.status_code == 200
