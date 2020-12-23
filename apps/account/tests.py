"""Tests for the account app."""
import pytest
from django.test import Client
from django.urls import reverse

from modularhistory.tests import TestSuite

unauthenticated_endpoints = ('login', 'register')
authenticated_endpoints = ('password_change', 'password_reset', 'profile', 'settings')


@pytest.mark.django_db
class AdminTestSuite(TestSuite):
    """Tests for the admin app."""

    def test_unauthenticated_endpoints(self):
        """Verify pages have 200 status."""
        client = Client()
        for endpoint in unauthenticated_endpoints:
            response = client.get(reverse(f'account:{endpoint}'))
            assert response.status_code == 200
