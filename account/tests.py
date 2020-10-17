"""Tests for the account app."""

import pytest
from hypothesis import example, given
from hypothesis.strategies import text


@pytest.mark.django_db
class TestNothing:
    """Tests for the account app."""

    do_nothing: bool = True

    @given(string=text())
    @example(string='Not doing anything')
    def test_nothing(self, string: str):
        """TODO: add docstring."""
        assert self.do_nothing
