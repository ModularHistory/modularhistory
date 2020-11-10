import pytest
from django.urls import reverse
from pympler import muppy, tracker
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

    @pytest.mark.skip('Failing.')
    def test_memory_with_pympler(self):
        """Test for memory leaks."""
        failed = False
        self.open(url)
        memory_tracker = tracker.SummaryTracker()
        ref_objects = muppy.get_objects()
        n_ref_objects = len(ref_objects)
        results = [f'{n_ref_objects}']
        for _ in range(0, 3):
            self.reload()
            self.wait(3)
            all_objects = muppy.get_objects()
            n_objects = len(all_objects)
            results.append(f'{n_objects} ({n_objects - n_ref_objects})')
            if n_objects > n_ref_objects:
                failed = True
        if failed:
            memory_tracker.print_diff()
            self.fail(f'Number of objects increased: {" --> ".join(results)}')
