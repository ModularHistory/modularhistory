import pytest
from django.urls import reverse
from hypothesis import given
from hypothesis.extra.django import from_model
from hypothesis.strategies import just, text

from apps.account.models import User
from modularhistory.tests import TestSuite


@pytest.mark.django_db
class AdminTestSuite(TestSuite):
    """Test suite for the homepage."""

    @given(from_model(User, is_staff=just(True)))
    def test_admin_site(self, user: User):
        """Test opening the admin site."""
        password = '80239gkhcqoqhmg8g94cm'  # noqa
        print('>>>>>>>>')
        print(user.username)
        # user = from_model(User, username=text, is_staff=just(True)).example()
        user.set_password(password)
        user.save()
        self.open(f'{self.base_url}{reverse("account:login")}')
        self.assert_element('body')
        self.assert_element('form')
        self.type('#id_username', user.username)
        self.type('#id_password', password)
        self.click('#submit-id-submit')
        self.wait(2)
        self.open(f'{self.base_url}/admin/')
        self.assert_element('body')
