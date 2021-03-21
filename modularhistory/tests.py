from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite
from hypothesis.extra.django import register_field_strategy
from hypothesis.strategies import just

from modularhistory.fields import HTMLField
from modularhistory.structures import HTML

register_field_strategy(HTMLField, just(HTML('lorem ipsum')))


class TestSuite:
    """Base class for test suites."""

    pass


class HypothesisTestSuite(TestSuite, DjangoHypothesisTestSuite):
    """Base class for test suites containing Hypothesis tests."""

    pass
