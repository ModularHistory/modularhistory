import pytest

from core.tests import TestSuite


@pytest.mark.django_db()
class TestPropositions(TestSuite):
    """Test the propositions app."""
