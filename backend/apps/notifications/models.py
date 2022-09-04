from django.conf import settings
from django.db import models


class Notification(models.Model):
    """A notification sent to a user."""

    recipient = models.ForeignKey(to=settings.AUTH_USER_MODEL)
    sent_date = models.DateTimeField()
    read = models.BooleanField(default=False)
