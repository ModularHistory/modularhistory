import pytest
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework.test import APIClient

from apps.flatpages.models import FlatPage
from apps.redirects.models import Redirect


@pytest.fixture()
def api_client():
    """Return an API client to be used in a test."""
    return APIClient()


@pytest.mark.django_db()
class TestFlatPages:
    """Test the flatpages app."""

    def test_adding_flatpage(self, api_client: APIClient):
        """Test adding a new flatpage."""
        original_path = '/flatpage/'
        original_url = reverse('flatpages_api:flatpage', kwargs={'path': original_path})
        new_path = '/newpath/'
        new_url = reverse('flatpages_api:flatpage', kwargs={'path': new_path})
        flatpage: FlatPage = FlatPage.objects.create(
            title='Flat Page',
            content='<p>This is a flat page.</p>',
            path=original_path,
            verified=True,
        )
        flatpage.sites.add(Site.objects.get(pk=settings.SITE_ID))
        assert FlatPage.objects.filter(path=original_path).exists()
        response = api_client.get(original_url)
        assert response.status_code == 200
        flatpage.path = new_path
        flatpage.save()
        response = api_client.get(new_url)
        assert response.status_code == 200
        assert Redirect.objects.filter(old_path=original_path, new_path=new_path).exists()
