import pytest

from apps.propositions.factories import PropositionFactory
from apps.propositions.models import Proposition
from core.tests import TestSuite


@pytest.mark.django_db()
class TestPropositions(TestSuite):
    """Test the propositions app."""

    def test_saving(self):
        """Verify pre-save and post-save logic runs correctly."""
        proposition: Proposition = PropositionFactory.build(
            slug='', cache={'testing': 'testing'}
        )
        assert not proposition.slug
        assert proposition.cache
        proposition.save()
        # Confirm slug was generated.
        assert proposition.slug
        # Confirm cache was wiped.
        assert not proposition.cache
