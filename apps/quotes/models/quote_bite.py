"""Quote bites."""

from typing import TYPE_CHECKING

from django.db import models

from apps.topics.models.taggable_model import TaggableModel

if TYPE_CHECKING:
    pass


class QuoteBite(TaggableModel):
    """A piece of a larger quote."""

    quote = models.ForeignKey(
        to='quotes.Quote', on_delete=models.CASCADE, related_name='bites'
    )
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
