import pytest
from django.urls import reverse

from modularhistory.constants.misc import ResponseCodes

EXPECTED_N_SQL_QUERIES = 15


@pytest.mark.django_db
def test_search(django_app, django_assert_max_num_queries):
    """Test that the search page loads successfully."""
    page = django_app.get(reverse('search'))
    assert page.status_code == ResponseCodes.SUCCESS
    page.mustcontain('<body>')
    assert 'form' in page
    with django_assert_max_num_queries(EXPECTED_N_SQL_QUERIES):
        django_app.get(reverse('search'))


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
