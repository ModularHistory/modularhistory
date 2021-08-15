"""Model classes for interviews."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.source import Source

INTERVIEWERS_MAX_LENGTH: int = 200


class Interview(Source):
    """An interview."""

    interviewers = models.CharField(
        verbose_name=_('interviewers'),
        max_length=INTERVIEWERS_MAX_LENGTH,
        blank=True,
    )

    def __html__(self) -> str:
        """Return the interview's citation HTML string."""
        components = [
            f'{self.attributee_html} to {self.interviewers or "interviewer"}',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
