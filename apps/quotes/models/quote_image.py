"""Quote images."""

from django.db import models

from modularhistory.models.positioned_relation import PositionedRelation


class QuoteImage(PositionedRelation):
    """An association of an image and a quote."""

    quote = models.ForeignKey(
        to='quotes.Quote', related_name='image_relations', on_delete=models.CASCADE
    )
    image = models.ForeignKey(to='images.Image', on_delete=models.PROTECT)

    def __str__(self):
        """Return the string representation of the quote–image association."""
        return f'{self.image} : {self.quote}'
