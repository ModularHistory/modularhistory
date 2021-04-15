"""Tests for the entities app."""

import pytest
from django.test import Client
from django.urls import reverse

from core.tests import TestSuite


@pytest.mark.django_db
class EntitiesTestSuite(TestSuite):
    """Tests for the admin app."""

    def test_entities(self):
        """Verify pages have 200 status."""
        client = Client()
        response = client.get(reverse('entities:index'))
        assert response.status_code == 200


# TODO: test that name_html matches regex in html_field
