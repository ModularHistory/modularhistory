# import pytest
# from hypothesis import example, given
# from hypothesis.strategies import text
from django.urls import reverse
from parameterized import parameterized
from seleniumbase import BaseCase

from modularhistory.constants import Environments
from modularhistory.settings import ENVIRONMENT

HOMEPAGE_URL = {
    Environments.DEV: 'http://127.0.0.1:8000',
    Environments.GITHUB_TEST: ' http://localhost:4444/wd/hub',
}


class HomepageTestSuite(BaseCase):
    """Test suite for the homepage."""

    def test_basic(self):
        self.open(f'{HOMEPAGE_URL.get(ENVIRONMENT)}/{reverse("home")}')
        # self.type('input[name="q"]', "xkcd book")
        # self.click('input[value="Search"]')
        # self.assert_text("xkcd: volume 0", "h3")
        # self.open("https://xkcd.com/353/")
        # self.assert_title("xkcd: Python")
        # self.assert_element('img[alt="Python"]')
        # self.click('a[rel="license"]')
        # self.assert_text("free to copy and reuse")
        # self.go_back()
        # self.click_link_text("About")
        # self.assert_exact_text("xkcd.com", "h2")
        # self.click_link_text("geohashing")
        # self.assert_element("#comic img")

    @parameterized.expand(
        [
            ['pypi', 'pypi.org'],
            ['wikipedia', 'wikipedia.org'],
            ['seleniumbase', 'seleniumbase/SeleniumBase'],
        ]
    )
    def test_parameterized_google_search(self, search_term, expected_text):
        self.open('https://google.com/ncr')
        # self.type('input[title="Search"]', search_term + '\n')
        # self.assert_element('#result-stats')
        # self.assert_text(expected_text, '#search')


# class MyTestClass(BaseCase):
#
#     def test_demo_site(self):
#         self.open("https://seleniumbase.io/demo_page.html")
#         self.assert_title("Web Testing Page")
#         self.assert_element("tbody#tbodyId")
#         self.assert_text("Demo Page", "h1")
#         self.type("#myTextInput", "This is Automated")
#         self.type("textarea.area1", "Testing Time!\n")
#         self.type('[name="preText2"]', "Typing Text!")
#         self.assert_text("Automation Practice", "h3")
#         self.hover_and_click("#myDropdown", "#dropOption2")
#         self.assert_text("Link Two Selected", "h3")
#         self.assert_text("This Text is Green", "#pText")
#         self.click("#myButton")
#         self.assert_text("This Text is Purple", "#pText")
#         self.assert_element('svg[name="svgName"]')
#         self.assert_element('progress[value="50"]')
#         self.press_right_arrow("#myslider", times=5)
#         self.assert_element('progress[value="100"]')
#         self.assert_element('meter[value="0.25"]')
#         self.select_option_by_text("#mySelect", "Set to 75%")
#         self.assert_element('meter[value="0.75"]')
#         self.assert_false(self.is_element_visible("img"))
#         self.switch_to_frame("#myFrame1")
#         self.assert_true(self.is_element_visible("img"))
#         self.switch_to_default_content()
#         self.assert_false(self.is_text_visible("iFrame Text"))
#         self.switch_to_frame("#myFrame2")
#         self.assert_true(self.is_text_visible("iFrame Text"))
#         self.switch_to_default_content()
#         self.assert_false(self.is_selected("#radioButton2"))
#         self.click("#radioButton2")
#         self.assert_true(self.is_selected("#radioButton2"))
#         self.assert_false(self.is_selected("#checkBox1"))
#         self.click("#checkBox1")
#         self.assert_true(self.is_selected("#checkBox1"))
#         self.assert_false(self.is_selected("#checkBox2"))
#         self.assert_false(self.is_selected("#checkBox3"))
#         self.assert_false(self.is_selected("#checkBox4"))
#         self.click_visible_elements("input.checkBoxClassB")
#         self.assert_true(self.is_selected("#checkBox2"))
#         self.assert_true(self.is_selected("#checkBox3"))
#         self.assert_true(self.is_selected("#checkBox4"))
#         self.assert_false(self.is_element_visible(".fBox"))
#         self.switch_to_frame("#myFrame3")
#         self.assert_true(self.is_element_visible(".fBox"))
#         self.assert_false(self.is_selected(".fBox"))
#         self.click(".fBox")
#         self.assert_true(self.is_selected(".fBox"))
#         self.switch_to_default_content()
#         self.assert_link_text("seleniumbase.com")
#         self.assert_link_text("SeleniumBase on GitHub")
#         self.assert_link_text("seleniumbase.io")
#         self.click_link_text("SeleniumBase Demo Page")
#         self.assert_exact_text("Demo Page", "h1")
