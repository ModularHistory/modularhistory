from django.conf import settings
from django.db import models

from apps.moderation.fields import SerializedObjectField


class ContentContribution(models.Model):
    """A contribution to a change."""

    contributor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='content_contributions',
        blank=True,
        null=True,
        editable=False,
    )
    change = models.ForeignKey(
        to='moderation.Change',
        on_delete=models.CASCADE,
        related_name='contributions',
        editable=False,
    )
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)
    content_before = SerializedObjectField()
    content_after = SerializedObjectField()

    def __str__(self) -> str:
        return f'Contribution by {self.contributor} to {self.change} ({self.date_created})'
