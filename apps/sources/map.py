from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.sources.models import Source

if TYPE_CHECKING:
    from django.db.models import QuerySet


class SourcesMap(Sitemap):
    """Sitemap for sources."""

    priority = 0.5

    def items(self) -> 'QuerySet[Source]':
        """Return the queryset of model instances to be included."""
        return Source.objects.filter(verified=True)
