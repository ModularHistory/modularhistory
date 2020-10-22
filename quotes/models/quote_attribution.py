"""Quote attributions."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, ForeignKey

from entities.models import Entity
from modularhistory.models import Model


class QuoteAttribution(Model):
    """TODO: add docstring."""

    quote = ForeignKey('quotes.Quote', related_name='attributions', on_delete=CASCADE)
    attributee = ForeignKey(
        Entity, related_name='quote_attributions', on_delete=CASCADE
    )
    position = models.PositiveSmallIntegerField(default=0, blank=True)

    class Meta:
        unique_together = ['quote', 'attributee']
        ordering = ['position']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return str(self.attributee)

    def clean(self):
        """TODO: write docstring."""
        super().clean()
        if self.position > 0:
            duplications = QuoteAttribution.objects.exclude(pk=self.pk).filter(
                quote=self.quote, attributee=self.attributee, position=self.position
            )
            if duplications.exists():
                raise ValidationError('Attribution position should be unique.')

    def save(self, *args, **kwargs):
        """TODO: write docstring."""
        self.clean()
        super().save(*args, **kwargs)
