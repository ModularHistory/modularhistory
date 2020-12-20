"""Tests for the entities app."""

from django.urls import reverse
from modularhistory.tests import TestSuite
from modularhistory.constants.misc import ResponseCodes
from django.test import Client


class EntitiesTestSuite(TestSuite):
    """Tests for the admin app."""

    def test_entities(self):
        """Verify pages have 200 status."""
        client = Client()
        response = client.get(reverse(f'entities:index'))
        assert response.status_code == 200


# TODO: test that name_html matches regex in html_field
