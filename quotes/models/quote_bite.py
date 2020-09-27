"""Quote bites."""

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import CASCADE, ForeignKey

from history.models import TaggableModel

if TYPE_CHECKING:
    pass


class QuoteBite(TaggableModel):
    """A piece of a larger quote."""

    quote = ForeignKey('quotes.Quote', on_delete=CASCADE, related_name='bites')
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
