import pytest
from django.urls import reverse

# from hypothesis import given, example
# from hypothesis.strategies import text
from django_webtest import WebTest

from modularhistory import settings


PERMANENT_REDIRECT = 301
SUCCESS = PERMANENT_REDIRECT if settings.SECURE_SSL_REDIRECT else 200


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
        """Test that the search page loads successfully."""
        page = self.app.get(reverse('search'))
        assert page.status_code == SUCCESS
        # page.mustcontain('<html>')
        assert 'form' in page
        # assert 'My Article' in page.click('Blog')
