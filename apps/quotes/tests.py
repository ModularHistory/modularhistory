"""Tests for the quotes app."""

from django.urls import reverse
from modularhistory.tests import TestSuite
from django.test import Client


class QuotesTestSuite(TestSuite):
    """Tests for the quotes app."""

    def test_entities(self):
        """Verify pages have 200 status."""
        client = Client()
        response = client.get(reverse('quotes:index'))
        assert response.status_code == 200
