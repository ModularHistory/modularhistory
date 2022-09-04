from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.quotes.models import Quote

if TYPE_CHECKING:
    from django.db.models import QuerySet


class QuotesMap(Sitemap):
    """Sitemap for quotes."""

    priority = 0.5

    def items(self) -> 'QuerySet[Quote]':
        """Return the queryset of model instances to be included."""
        return Quote.objects.filter(verified=True)
