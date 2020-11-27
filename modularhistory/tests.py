"""Tests for the whole ModularHistory application."""

import pytest

from modularhistory.constants.misc import ResponseCodes

# def test_app_inclusion():
#     """Test that the entities page loads successfully."""
#     page = django_app.get(reverse('entities:index'))
#     assert page.status_code == ResponseCodes.SUCCESS
#     page.mustcontain('<body>')
#     with django_assert_max_num_queries(EXPECTED_N_SQL_QUERIES):
#         django_app.get(reverse('entities:index'))
