from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.entities.models import Entity

if TYPE_CHECKING:
    from django.db.models import QuerySet


class EntitiesMap(Sitemap):
    """Sitemap for entities."""

    priority = 0.5

    def items(self) -> 'QuerySet[Entity]':
        """Return the queryset of model instances to be included."""
        return Entity.objects.filter(verified=True)
