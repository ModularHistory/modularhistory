from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.model import ExtendedModel
from core.utils.string import truncate


class Chat(models.Model):
    """A chat between volunteers/contributors/staff."""

    content = models.TextField(verbose_name=_('chat'))

    def __str__(self) -> str:
        """Return the chat's string representation."""
        return truncate(self.content)
