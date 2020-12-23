from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite
from hypothesis.extra.django import register_field_strategy
from hypothesis.strategies import just
from seleniumbase import BaseCase as SeleniumTestSuite

from modularhistory.constants.misc import Environments
from modularhistory.environment import environment
from modularhistory.fields import HTMLField
from modularhistory.structures import HTML

register_field_strategy(HTMLField, just(HTML('lorem ipsum')))

BASE_URLS = {
    Environments.DEV: 'http://localhost:8000',
}


class TestSuite:
    """Base class for test suites."""

    base_url = BASE_URLS.get(environment) or BASE_URLS[Environments.DEV]


class HypothesisTestSuite(TestSuite, DjangoHypothesisTestSuite):
    """Base class for test suites containing Hypothesis tests."""

    pass


class UserInterfaceTestSuite(TestSuite, SeleniumTestSuite):
    """Base class for UI test suites."""

    pass
