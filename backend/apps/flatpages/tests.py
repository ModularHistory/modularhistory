import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.flatpages.factories import FlatPageFactory
from apps.flatpages.models import FlatPage
from apps.redirects.models import Redirect


@pytest.mark.django_db()
class TestFlatPages:
    """Test the flatpages app."""

    def test_changing_flatpage_path(self, api_client: APIClient):
        """
        Test adding a new flatpage and then changing its path.

        When the flatpage's path is changed, a redirect should be created
        from the page's prior path to its new path.
        """
        flatpage: FlatPage = FlatPageFactory.create()
        original_path = flatpage.path
        original_url = reverse('flatpages_api:flatpage', kwargs={'path': original_path})
        # Confirm the flatpage can be retrieved by its path.
        assert FlatPage.objects.filter(path=original_path).exists()
        response = api_client.get(original_url)
        assert response.status_code == 200

        # Change the flatpage's path.
        new_path = '/new/path'
        new_url = reverse('flatpages_api:flatpage', kwargs={'path': new_path})
        flatpage.path = new_path
        flatpage.save(moderate=False)

        # Confirm the flatpage can be retrieved by its new path.
        response = api_client.get(new_url)
        assert response.status_code == 200

        # Confirm a redirect was created.
        assert Redirect.objects.filter(old_path=original_path, new_path=new_path).exists()
