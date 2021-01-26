import pytest
from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite
from hypothesis.extra.django import register_field_strategy
from hypothesis.strategies import just

from modularhistory.constants.environments import Environments
from modularhistory.fields import HTMLField
from modularhistory.structures import HTML

register_field_strategy(HTMLField, just(HTML('lorem ipsum')))

BASE_URLS = {
    Environments.DEV: 'http://localhost',
}


class TestSuite:
    """Base class for test suites."""

    pass


class HypothesisTestSuite(TestSuite, DjangoHypothesisTestSuite):
    """Base class for test suites containing Hypothesis tests."""

    pass


class UserInterfaceTestSuite(TestSuite):
    """Base class for UI test suites."""

    base_url: str

    @pytest.fixture(autouse=True)
    def _setup_ui_test(self, live_server, sb):
        """Set necessary test attributes and attach the Selenium client."""
        self.base_url = live_server.url
        self.client = sb
