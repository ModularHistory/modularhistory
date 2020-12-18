"""Tests for the account app."""
import pytest
from django.test import Client
from django.urls import reverse

unauthenticated_endpoints = ('login', 'register')
authenticated_endpoints = ('password_change', 'password_reset', 'profile', 'settings')


@pytest.mark.django_db
def test_unauthenticated_endpoints(client: Client):
    """Verify pages have 200 status."""
    for endpoint in unauthenticated_endpoints:
        response = client.get(reverse(f'account:{endpoint}'))
        assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_endpoints(client: Client):
    """Verify pages have 200 status."""
    pass
