"""Model classes for web pages."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.mixins.textual import TextualMixin
from apps.sources.models.publication import AbstractPublication
from apps.sources.models.source import PolymorphicSource


class Website(AbstractPublication):
    """A website."""

    owner = models.CharField(
        verbose_name=_('owner'), max_length=100, null=True, blank=True
    )


class PolymorphicWebPage(PolymorphicSource, TextualMixin):
    """A web page."""

    website = models.ForeignKey(
        'sources.Website', null=True, blank=True, on_delete=models.CASCADE
    )
