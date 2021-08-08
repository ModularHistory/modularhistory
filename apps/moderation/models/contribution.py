from django.conf import settings
from django.db import models


class ContentContribution(models.Model):
    """A contribution to a change."""

    contributor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name='content_contributions',
    )
    change = models.ForeignKey(
        to='moderation.Change',
        editable=False,
        on_delete=models.CASCADE,
        related_name='contributions',
    )

    def __str__(self) -> str:
        return f'Contribution by {self.contributor} to {self.change}'
