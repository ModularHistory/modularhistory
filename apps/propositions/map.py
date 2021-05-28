from django.contrib.sitemaps import Sitemap

from apps.propositions.models import TypedProposition


class PropositionSitemap(Sitemap):
    """Sitemap for propositions."""

    priority = 0.6

    def items(self):
        """Return the queryset of model instances to be included."""
        return TypedProposition.objects.filter(verified=True, hidden=False)
