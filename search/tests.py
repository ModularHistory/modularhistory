import pytest
from django.urls import reverse
from django_webtest import WebTest

from modularhistory.constants import ResponseCodes


@pytest.mark.django_db
class TestSearch(WebTest):
    """Test the search app."""

    def test_search(self):
        """Test that the search page loads successfully."""
        page = self.app.get(reverse('search'))
        assert page.status_code == ResponseCodes.SUCCESS
        page.mustcontain('<body>')
        assert 'form' in page
