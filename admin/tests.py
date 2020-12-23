import string

import pytest
from django.urls import reverse
from hypothesis.extra.django import from_model
from hypothesis.strategies import just, text

from apps.account.models import User
from modularhistory.tests import UserInterfaceTestSuite

VALID_PASSWORD_CHARACTERS = string.ascii_letters + string.digits + '!@#$%^&*()-_=+.,'


@pytest.mark.django_db
class AdminTestSuite(UserInterfaceTestSuite):
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
        self.client.wait(10)
        self.client.open(f'{self.base_url}{reverse("account:login")}')
        self.client.assert_element('body')
        self.client.assert_element('form')
        self.client.wait(10)
        self.client.type('#id_username', user.username)
        self.client.type('#id_password', password)
        self.client.click('#submit-id-submit')
        self.client.wait(10)
        self.client.open(f'{self.base_url}/admin/')
        self.client.assert_element('body')
