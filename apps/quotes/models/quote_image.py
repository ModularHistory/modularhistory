"""Quote images."""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from modularhistory.models.positioned_relation import PositionedRelation


class QuoteImage(PositionedRelation):
    """An association of an image and a quote."""

    quote = models.ForeignKey(
        to='quotes.Quote',
        on_delete=models.CASCADE,
        related_name='image_relations',
        verbose_name=_('quote'),
    )
    image = models.ForeignKey(
        to='images.Image',
        on_delete=models.PROTECT,
        related_name='quote_relations',
        verbose_name=_('image'),
    )

    def __str__(self):
        """Return the string representation of the quote–image association."""
        return f'{self.image} : {self.quote}'
