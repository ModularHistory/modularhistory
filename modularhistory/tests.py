from hypothesis.extra.django import TestCase as DjangoHypothesisTestSuite
from hypothesis.extra.django import register_field_strategy
from hypothesis.strategies import just
from seleniumbase import BaseCase as SeleniumTestSuite

from modularhistory.constants.misc import Environments
from modularhistory.environment import environment
from modularhistory.fields import HTMLField
from modularhistory.structures import HTML

register_field_strategy(HTMLField, just(HTML('lorem ipsum')))

BASE_URL = {
    Environments.DEV: 'http://127.0.0.1:8000',
    Environments.GITHUB_TEST: ' http://localhost:4444/wd/hub',
}


class TestSuite(DjangoHypothesisTestSuite):
    """Test suite for the homepage."""

    base_url = BASE_URL.get(environment)


class UserInterfaceTestSuite(TestSuite, SeleniumTestSuite):
    """Base class for UI test suites."""

    pass
