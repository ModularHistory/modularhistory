"""Tests for the quotes app."""

import pytest
from django.test import Client
from django.urls import reverse

from modularhistory.tests import TestSuite


@pytest.mark.django_db
class QuotesTestSuite(TestSuite):
    """Tests for the quotes app."""

    def test_quotes(self):
        """Verify pages have 200 status."""
        client = Client()
        response = client.get(reverse('quotes:index'))
        assert response.status_code == 200
