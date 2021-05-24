from django_perf_rec import TestCaseMixin
from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite


class TestSuite(TestCaseMixin):
    """Base class for test suites."""


class HypothesisTestSuite(TestSuite, DjangoHypothesisTestSuite):
    """Base class for test suites containing Hypothesis tests."""
