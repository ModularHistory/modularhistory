import pytest
from django.urls import reverse
from hypothesis.extra.django import from_model
from hypothesis.strategies import just

from account.models import User
from modularhistory.constants import ResponseCodes


@pytest.mark.django_db
def test_admin(django_app):
    """Test that the search page loads successfully."""
    password = '80239gkhcqoqhmg8g94cm'  # noqa
    user = from_model(User, is_staff=just(True)).example()
    user.set_password(password)
    user.save()
    page = django_app.get(reverse('account:login'))
    page.mustcontain('<body>')
    form = page.form
    form['username'] = user.username
    form['password'] = password
    form.submit()
    page = django_app.get('/admin/')
