from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.flatpages.models import FlatPage

if TYPE_CHECKING:
    from django.db.models import QuerySet


class FlatPagesMap(Sitemap):
    """Sitemap for flatpages."""

    priority = 0.5

    def items(self) -> 'QuerySet[FlatPage]':
        """Return the queryset of model instances to be included."""
        return FlatPage.objects.filter(verified=True)
