import pytest

from sources.models import Source


# from hypothesis import assume, given
# from hypothesis.extra.django import from_model
# from hypothesis.strategies import text


@pytest.mark.django_db
class TestSources:
    """Test the sources app."""

    @pytest.mark.parametrize('source_type', ['sources.book', 'sources.article'])
    # @given(title=text())
    def test_source(self, source_type: str):
        """TODO: add docstring."""
        title = f'asdf {source_type}'
        source = Source(
            type=source_type,
            title=title
        )
        source.recast(source_type)
        source.save()
        print(source)
        assert len(f'{source}')
