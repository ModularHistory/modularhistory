import pytest

from sources.models import Source


@pytest.mark.django_db
class TestSources:
    """Test the sources app."""

    @pytest.mark.parametrize('source_type', ['sources.book'])
    def test_source_creation(self, source_type: str):
        """Test creation of sources."""
        title = f'asdf {source_type}'
        source = Source(type=source_type, title=title)
        source.recast(source_type)
        source.save()
        print(source)
        assert len(f'{source}')

    # TODO: Test that all kinds of sources are included in search results
