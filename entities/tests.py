"""Tests for the entities app."""

import pytest
from django.urls import reverse

from modularhistory.constants.misc import ResponseCodes

EXPECTED_N_SQL_QUERIES = 15


@pytest.mark.django_db
def test_entities(django_app, django_assert_max_num_queries):
    """Test that the entities page loads successfully."""
    page = django_app.get(reverse('entities:index'))
    assert page.status_code == ResponseCodes.SUCCESS
    page.mustcontain('<body>')
    assert 'form' in page
    with django_assert_max_num_queries(EXPECTED_N_SQL_QUERIES):
        django_app.get(reverse('entities:index'))
