from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.propositions.models import PolymorphicProposition

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PropositionSitemap(Sitemap):
    """Sitemap for propositions."""

    priority = 0.6

    def items(self) -> 'QuerySet[PolymorphicProposition]':
        """Return the queryset of model instances to be included."""
        return PolymorphicProposition.objects.filter(verified=True, hidden=False)
