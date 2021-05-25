import pytest

from apps.propositions.models.proposition import TypedProposition
from core.tests import TestSuite


@pytest.mark.django_db()
class TestPropositions(TestSuite):
    """Test the propositions app."""

    def test_query_performance(self):
        """Test the performance of a simple query."""
        with self.record_performance():
            list(TypedProposition.objects.all())
