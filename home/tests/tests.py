from django.urls import reverse
from seleniumbase import BaseCase

from modularhistory.constants.misc import Environments
from modularhistory.settings import ENVIRONMENT

HOMEPAGE_URL = {
    Environments.DEV: 'http://127.0.0.1:8000',
    Environments.GITHUB_TEST: ' http://localhost:4444/wd/hub',
}

url = f'{HOMEPAGE_URL.get(ENVIRONMENT)}{reverse("home")}'

TRACEMALLOC, PYMPLER = 'tracemalloc', 'pympler'


class HomepageTestSuite(BaseCase):
    """Test suite for the homepage."""

    def test_opening_homepage(self):
        """Test opening the homepage."""
        self.open(url)
