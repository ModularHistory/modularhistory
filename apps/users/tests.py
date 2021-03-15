"""Tests for the users app."""
import pytest
from django.test import Client
from django.urls import reverse

from modularhistory.tests import TestSuite

unauthenticated_endpoints = ('login', 'register')
authenticated_endpoints = ('password_change', 'password_reset', 'profile', 'settings')

ACCEPTABLE_STATUS_CODES = (200, 301)


@pytest.mark.django_db
class UsersTestSuite(TestSuite):
    """Tests for the users app."""

    def test_unauthenticated_endpoints(self):
        """Verify pages have 200 status."""
        client = Client()
        for endpoint in unauthenticated_endpoints:
            response = client.get(reverse(f'users:{endpoint}'))
            assert response.status_code in ACCEPTABLE_STATUS_CODES
