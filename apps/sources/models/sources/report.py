"""Model classes for reports (as sources)."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.mixins.textual import TextualMixin
from apps.sources.models.source import Source


class Report(Source, TextualMixin):
    """A report published by a government, task group, or other organization."""

    publisher = models.CharField(
        verbose_name=_('publisher'),
        max_length=100,
        help_text='the organization that published the report',
    )
    number = models.PositiveSmallIntegerField(
        verbose_name=_('report number'),
        null=True,
        blank=True,
    )

    def __html__(self) -> str:
        """Return the report's HTML representation."""
        identifier = f'<i>{self.linked_title}</i>' if self.title else 'untitled report'
        if self.number:
            identifier += f' (Report No. {self.number})'
        components = [
            self.attributee_html,
            identifier,
            self.publisher,
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
