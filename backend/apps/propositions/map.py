from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.propositions.models import Proposition

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PropositionsMap(Sitemap):
    """Sitemap for propositions."""

    priority = 0.6

    def items(self) -> 'QuerySet[Proposition]':
        """Return the queryset of model instances to be included."""
        return Proposition.objects.filter(verified=True)
