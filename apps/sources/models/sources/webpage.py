"""Model classes for webpages."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.mixins.textual import TextualMixin
from apps.sources.models.publication import AbstractPublication
from apps.sources.models.source import Source


class Website(AbstractPublication):
    """A website."""

    owner = models.CharField(
        verbose_name=_('owner'), max_length=80, null=True, blank=True
    )


class Webpage(Source, TextualMixin):
    """A webpage."""

    website = models.ForeignKey(
        to='sources.Website', null=True, blank=True, on_delete=models.CASCADE
    )

    date_nullable = True

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        components = [
            self.attributee_html,
            f'"{self.linked_title}"',
            f'<i>{self.website.name}</i>',
            self.website.owner,
            self.date.string if self.date else '',
            f'retrieved from <a target="_blank" href="{self.url}" class="url">{self.url}</a>',
        ]
        return self.components_to_html(components)
