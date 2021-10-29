from typing import TYPE_CHECKING

from django.contrib.sitemaps import Sitemap

from apps.images.models import Image

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ImagesMap(Sitemap):
    """Sitemap for images."""

    priority = 0.5

    def items(self) -> 'QuerySet[Image]':
        """Return the queryset of model instances to be included."""
        return Image.objects.filter(verified=True)
