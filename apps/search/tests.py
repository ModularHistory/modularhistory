import pytest
from django.urls import reverse
from parameterized import parameterized

from modularhistory.tests import UserInterfaceTestSuite

EXPECTED_N_SQL_QUERIES = 15


@pytest.mark.django_db
class SearchTestSuite(UserInterfaceTestSuite):
    """Test suite for the homepage."""

    def test_empty_search(self, live_server):
        """Test opening the homepage."""
        self.client.open(f'{self.base_url}{reverse("search")}')
        self.client.assert_element('body')
        self.client.assert_element('form')

    @parameterized.expand(['conservatism', 'liberalism'])
    def test_search_with_query(self, query: str):
        """Test that the search page loads successfully with queries."""
        self.client.open(f'{self.base_url}{reverse("search")}?query={query}')
        self.client.assert_element('body')
        self.client.assert_element('form')
