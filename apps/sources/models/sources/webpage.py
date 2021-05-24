"""Model classes for webpages."""

from django.core.exceptions import ValidationError
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

    def __str__(self) -> str:
        return self.name


class Webpage(Source, TextualMixin):
    """A webpage."""

    website_name = models.CharField(max_length=20, blank=True)
    website = models.ForeignKey(
        to='sources.Website', null=True, blank=True, on_delete=models.CASCADE
    )

    date_nullable = True

    def clean(self):
        super().clean()
        if not self.website and not self.website_name:
            raise ValidationError('Please specify either `website` or `website_name`.')

    def save(self, *args, **kwargs):
        self.website_name = self.website.name if self.website else self.website_name
        super().save(*args, **kwargs)

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        components = [
            self.attributee_html,
            f'"{self.linked_title}"',
            f'<i>{self.website_name}</i>' if self.website_name else '',
            self.website.owner,
            self.date.string if self.date else '',
            f'retrieved from <a target="_blank" href="{self.url}" class="url">{self.url}</a>',
        ]
        return self.components_to_html(components)
