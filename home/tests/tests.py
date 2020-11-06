import linecache
import tracemalloc

import pytest
from blackfire import probe
from django.urls import reverse
from parameterized import parameterized
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

    @pytest.mark.skip('Useless.')
    def test_memory_with_tracemalloc(self):
        """Test for memory leaks."""
        self.open(url)
        ref_snapshot = tracemalloc.take_snapshot()
        for _ in range(0, 5):
            self.reload()
            self.wait(3)
            snapshot = tracemalloc.take_snapshot()
            traces = snapshot.statistics('traceback')
            for index, stat in enumerate(
                snapshot.compare_to(ref_snapshot, 'lineno')[:15]
            ):
                diff = f'{stat}'
                filters = (
                    '<frozen importlib._bootstrap' not in diff,
                    'linecache' not in diff,
                    'autoreload.py' not in diff,
                    'sre_parse.py' not in diff,
                    'pympler' not in diff,
                    'tracemalloc' not in diff,
                    'pytest' not in diff,
                    'webdriver' not in diff,
                    'connectionpool.py' not in diff,
                    'poolmanager.py' not in diff,
                    'tokenize.py' not in diff,
                    'client.py' not in diff,
                    'parse.py',
                )
                if all(filters):
                    print(diff)
                    trace = traces[index]
                    print('%s memory blocks: %.1f KiB' % (stat.count, stat.size / 1024))
                    for line in trace.traceback.format():
                        if '_pytest' not in line and '_bootstrap' not in line:
                            print(line)
                    print()
                # display_top(snapshot)

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

    @pytest.mark.skip(reason='Blackfire requires per-env configuration.')
    def test_memory_with_blackfire(self):
        self.open(url)
        with probe.run():
            for _ in range(0, 5):
                self.reload()
                self.wait(3)

    @pytest.mark.skip
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


def display_top(snapshot, key_type='lineno', limit=15):
    snapshot = snapshot.filter_traces(
        (
            tracemalloc.Filter(False, '<frozen importlib._bootstrap>'),
            tracemalloc.Filter(False, '<frozen importlib._bootstrap_external>'),
            tracemalloc.Filter(False, '<unknown>'),
        )
    )
    top_stats = snapshot.statistics(key_type)

    print('Top %s lines' % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        print(
            '#%s: %s:%s: %.1f KiB'
            % (index, frame.filename, frame.lineno, stat.size / 1024)
        )
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print('%s other: %.1f KiB' % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print('Total allocated size: %.1f KiB' % (total / 1024))
