# import pytest
# from hypothesis import example, given
# from hypothesis.strategies import text
from pympler import tracker, muppy, refbrowser
from django.urls import reverse
from parameterized import parameterized
from seleniumbase import BaseCase

from modularhistory.constants import Environments
from modularhistory.constants.strings import NEW_LINE
from modularhistory.settings import ENVIRONMENT

HOMEPAGE_URL = {
    Environments.DEV: 'http://127.0.0.1:8000',
    Environments.GITHUB_TEST: ' http://localhost:4444/wd/hub',
}

url = f'{HOMEPAGE_URL.get(ENVIRONMENT)}{reverse("home")}'


class HomepageTestSuite(BaseCase):
    """Test suite for the homepage."""

    def test_opening_homepage(self):
        """Test opening the homepage."""
        self.open(url)

    def test_memory_consumption(self):
        """Test for memory leaks."""
        self.open(url)
        memory_tracker = tracker.SummaryTracker()
        ref_objects = muppy.get_objects()
        n_ref_objects = len(ref_objects)
        for _ in range(0, 5):
            self.reload()
            all_objects = muppy.get_objects()
            n_objects = len(all_objects)
            if n_objects > n_ref_objects:
                for object_type in all_objects:
                    print(object_type)
                memory_tracker.print_diff()
                self.fail(
                    f'Number of objects increased by {n_objects - n_ref_objects}.'
                )

    @parameterized.expand(
        [
            ['pypi', 'pypi.org'],
            ['wikipedia', 'wikipedia.org'],
        ]
    )
    def test_parameterized_google_search(self, search_term, expected_text):
        self.open('https://google.com/ncr')
        # self.type('input[title="Search"]', search_term + '\n')
        # self.assert_element('#result-stats')
        # self.assert_text(expected_text, '#search')
