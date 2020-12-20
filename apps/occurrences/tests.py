"""Tests for the occurrences app."""

from django.urls import reverse
from modularhistory.tests import TestSuite
from django.test import Client


class OccurrencesTestSuite(TestSuite):
    """Tests for the occurrences app."""

    def test_occurrences(self):
        """Verify pages have 200 status."""
        client = Client()
        response = client.get(reverse('occurrences:index'))
        assert response.status_code == 200
