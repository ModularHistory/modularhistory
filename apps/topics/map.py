from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.topics.models import Topic

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TopicsMap(Sitemap):
    """Sitemap for topics."""

    priority = 0.5

    def items(self) -> 'QuerySet[Topic]':
        """Return the queryset of model instances to be included."""
        return Topic.objects.filter(verified=True)
