"""Model classes for interviews."""

from django.db import models

from apps.sources.models import PolymorphicSource

INTERVIEWERS_MAX_LENGTH: int = 200


class Interview(PolymorphicSource):
    """An interview."""

    interviewers = models.CharField(
        max_length=INTERVIEWERS_MAX_LENGTH, null=True, blank=True
    )

    def __html__(self) -> str:
        """Return the interview's citation HTML string."""
        components = [
            f'{self.attributee_html} to {self.interviewers or "interviewer"}',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
