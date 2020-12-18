import string

import pytest
from django.urls import reverse
from hypothesis import given
from hypothesis.extra.django import from_model
from hypothesis.strategies import just, text

from apps.account.models import User
from modularhistory.tests import TestSuite

VALID_PASSWORD_CHARACTERS = string.ascii_letters + string.digits + '!@#$%^&*()-_=+.,'


@pytest.mark.django_db
class AdminTestSuite(TestSuite):
    """Test suite for the homepage."""

    def test_admin_site(self):
        """Test opening the admin site."""
        user = from_model(
            User,
            username=text(alphabet=VALID_PASSWORD_CHARACTERS, min_size=6, max_size=20),
            is_staff=just(True),
        ).example()
        password = text(
            alphabet=VALID_PASSWORD_CHARACTERS, min_size=7, max_size=27
        ).example()
        user.set_password(password)
        user.save()
        self.wait(10)
        self.open(f'{self.base_url}{reverse("account:login")}')
        self.assert_element('body')
        self.assert_element('form')
        self.wait(10)
        self.type('#id_username', user.username)
        self.type('#id_password', password)
        self.click('#submit-id-submit')
        self.wait(10)
        self.open(f'{self.base_url}/admin/')
        self.assert_element('body')
