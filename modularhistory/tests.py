from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite
from hypothesis.extra.django import register_field_strategy
from hypothesis.strategies import just
from django.test import LiveServerTestCase as LiveServerTestSuite
from modularhistory.constants.misc import Environments
from modularhistory.environment import environment
from modularhistory.fields import HTMLField
from modularhistory.structures import HTML
import pytest

register_field_strategy(HTMLField, just(HTML('lorem ipsum')))

BASE_URLS = {
    Environments.DEV: 'http://localhost:8001',
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
    def setup_ui_test(self, live_server, sb):
        self.base_url = live_server.url
        self.client = sb
