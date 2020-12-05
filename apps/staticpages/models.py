from django.contrib.flatpages.models import FlatPage
from django.db import models

META_DESCRIPTION_MAX_LENGTH: int = 200


class AbstractFlatPage(FlatPage):
    """Abstract base class for static pages."""

    class Meta:
        abstract = True


class StaticPage(AbstractFlatPage):
    """A static page (e.g., about page, privacy policy page, etc.)."""

    meta_description = models.TextField(max_length=META_DESCRIPTION_MAX_LENGTH)

    class Meta:
        ordering = ['url']
