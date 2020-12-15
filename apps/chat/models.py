from django.db import models
from modularhistory.models.model import Model
from django.utils.translation import ugettext_lazy as _


class Chat(Model):
    """A chat between volunteers/contributors/staff."""

    content = models.TextField(verbose_name=_('chat'))
