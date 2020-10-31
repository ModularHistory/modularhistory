from seleniumbase import BaseCase


class BaseTestCase(BaseCase):
    def setUp(self):
        super().setUp()
        # <<< Run custom code AFTER the super() line >>>

    def tearDown(self):
        self.save_teardown_screenshot()
        if self.has_exception():
            # <<< Run custom code if the test failed. >>>
            pass
        else:
            # <<< Run custom code if the test passed. >>>
            pass
        # (Wrap unreliable code in a try/except block.)
        # <<< Run custom code BEFORE the super() line >>>
        super().tearDown()

    def login(self):
        # <<< Placeholder. Add your code here. >>>
        pass

    def example_method(self):
        # <<< Placeholder. Add your code here. >>>
        pass
