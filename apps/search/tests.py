import pytest
from django.urls import reverse
from parameterized import parameterized

from modularhistory.tests import UserInterfaceTestSuite

EXPECTED_N_SQL_QUERIES = 15


class SearchTestSuite(UserInterfaceTestSuite):
    """Test suite for the homepage."""

    def test_empty_search(self):
        """Test opening the homepage."""
        self.open(f'{self.base_url}{reverse("search")}')
        self.assert_element('body')
        self.assert_element('form')

    @parameterized.expand(['conservatism', 'liberalism'])
    def test_search_with_query(self, query: str):
        """Test that the search page loads successfully with queries."""
        self.open(f'{self.base_url}{reverse("search")}?query={query}')
        self.assert_element('body')
        self.assert_element('form')
