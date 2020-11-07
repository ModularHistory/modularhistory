"""Quote attributions."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, ForeignKey

from entities.models import Entity
from modularhistory.models import Model


class QuoteAttribution(Model):
    """An attribution of a quote to an entity."""

    quote = ForeignKey('quotes.Quote', related_name='attributions', on_delete=CASCADE)
    attributee = ForeignKey(
        Entity, related_name='quote_attributions', on_delete=CASCADE
    )
    position = models.PositiveSmallIntegerField(default=0, blank=True)

    class Meta:
        unique_together = ['quote', 'attributee']
        ordering = ['position']

    def __str__(self) -> str:
        """Return the string representation of the quote attribution."""
        return str(self.attributee)

    def save(self, *args, **kwargs):
        """Save the quote attribution to the database."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Prepare the quote attribution to be saved."""
        super().clean()
        if self.position > 0:
            duplications = QuoteAttribution.objects.exclude(pk=self.pk).filter(
                quote=self.quote, attributee=self.attributee, position=self.position
            )
            if duplications.exists():
                raise ValidationError('Attribution position should be unique.')
