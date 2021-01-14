"""Tests for the occurrences app."""

import pytest
from django.test import Client
from django.urls import reverse

from modularhistory.tests import TestSuite


@pytest.mark.django_db
class OccurrencesTestSuite(TestSuite):
    """Tests for the occurrences app."""

    def test_occurrences(self):
        """Verify pages have 200 status."""
        client = Client()
        response = client.get(reverse('occurrences:index'))
        assert response.status_code == 200
