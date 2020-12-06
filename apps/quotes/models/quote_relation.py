from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from modularhistory.models.positioned_relation import PositionedRelation
from modularhistory.utils.html import soupify


class QuoteRelation(PositionedRelation):
    """A relation to a quote (by any other model)."""

    quote = models.ForeignKey(
        to='quotes.Quote', related_name='relations', on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        """
        Meta options for QuoteRelation.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """
        unique_together = ['quote', 'content_type', 'object_id', 'position']
        ordering = ['position', 'quote']

    def __str__(self) -> str:
        """Return the string representation of the relation."""
        return soupify(self.quote.bite.html).get_text()

    @property
    def quote_pk(self) -> str:
        """
        Return the primary key of the quote relation's quote.

        This attribute can be included in inline admins.
        """
        return self.quote.pk
