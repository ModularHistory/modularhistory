import pytest
from django.urls import reverse
from django_webtest import WebTest

from modularhistory import settings

PERMANENT_REDIRECT = 301
SUCCESS = PERMANENT_REDIRECT if settings.SECURE_SSL_REDIRECT else 200


@pytest.mark.django_db
class TestSearch(WebTest):
    """TODO: add docstring."""

    def test_search(self):
        """Test that the search page loads successfully."""
        page = self.app.get(reverse('search'))
        assert page.status_code == SUCCESS
        page.mustcontain('<body>')
        assert 'form' in page
