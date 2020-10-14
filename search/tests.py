import pytest
# from hypothesis import given, example
# from hypothesis.strategies import text
from django_webtest import WebTest
from django.urls import reverse
from modularhistory import settings

SUCCESS = 200
PERMANENT_REDIRECT = 301


# @pytest.mark.django_db
# class TestNothing:
#     """TODO: add docstring."""
#
#     do_nothing: bool = True
#
#     @given(string=text())
#     @example(string='Not doing anything')
#     def test_nothing(self, string: str):
#         """TODO: add docstring."""
#         assert self.do_nothing


@pytest.mark.django_db
class TestSearch(WebTest):
    """TODO: add docstring."""

    def test_search(self):
        response = self.app.get(reverse('search'))
        if settings.SECURE_SSL_REDIRECT:
            assert response.status_code == PERMANENT_REDIRECT
        else:
            assert response.status_code == SUCCESS
