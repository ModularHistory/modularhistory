import pytest
from hypothesis import given, example
from hypothesis.strategies import text


@pytest.mark.django_db
class TestNothing:
    """Test the images app."""

    do_nothing: bool = True

    @given(string=text())
    @example(string='Not doing anything')
    def test_nothing(self, string: str):
        """TODO: add docstring."""
        assert self.do_nothing
