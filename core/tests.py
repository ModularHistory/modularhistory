from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite
from hypothesis.extra.django import register_field_strategy
from hypothesis.strategies import just

from core.fields import HTMLField
from core.structures import HTML

register_field_strategy(HTMLField, just(HTML('lorem ipsum')))


class TestSuite:
    """Base class for test suites."""


class HypothesisTestSuite(TestSuite, DjangoHypothesisTestSuite):
    """Base class for test suites containing Hypothesis tests."""
