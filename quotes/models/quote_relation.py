from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import CASCADE, ForeignKey, PositiveSmallIntegerField

from history.models import Model

if TYPE_CHECKING:
    pass


class QuoteRelation(Model):
    """A relation to a quote (by any other model)."""

    quote = ForeignKey('quotes.Quote', related_name='relations', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    position = PositiveSmallIntegerField(
        null=True, blank=True,  # TODO: add cleaning logic
        help_text='Determines the order of quotes.'
    )

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.quote.bite.html, features='lxml').get_text()

    class Meta:
        unique_together = ['quote', 'content_type', 'object_id', 'position']
        ordering = ['position', 'quote']

    @property
    def quote_pk(self) -> str:
        return self.quote.pk
