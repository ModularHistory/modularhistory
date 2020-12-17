import pytest
from django.urls import reverse

from modularhistory.constants.misc import ResponseCodes

from django.urls import reverse
from seleniumbase import BaseCase

from modularhistory.constants.misc import Environments
from modularhistory.settings import ENVIRONMENT

EXPECTED_N_SQL_QUERIES = 15


HOMEPAGE_URL = {
    Environments.DEV: 'http://127.0.0.1:8000',
    Environments.GITHUB_TEST: ' http://localhost:4444/wd/hub',
}

url = f'{HOMEPAGE_URL.get(ENVIRONMENT)}{reverse("search")}'


# class SearchTestSuite(BaseCase):
#     """Test suite for the homepage."""

#     def test_opening_homepage(self):
#         """Test opening the homepage."""
#         self.open(url)


@pytest.mark.django_db
def test_empty_search(django_app, django_assert_max_num_queries):
    """Test that the search page loads successfully."""
    page = django_app.get(reverse('search'))
    assert page.status_code == ResponseCodes.SUCCESS
    page.mustcontain('<body>')
    assert 'form' in page


@pytest.mark.django_db
@pytest.mark.parametrize('query', ['conservatism', 'liberalism'])
def test_search_with_query(django_app, django_assert_max_num_queries, query: str):
    """Test that the search page loads successfully with queries."""
    url = f'{reverse("search")}?query={query}'
    page = django_app.get(url)
    with django_assert_max_num_queries(EXPECTED_N_SQL_QUERIES):
        django_app.get(url)
    assert page.status_code == ResponseCodes.SUCCESS

    assert 'form' in page
