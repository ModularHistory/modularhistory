"""Quote attributions."""

from django.core.exceptions import ValidationError
from django.db import models

from modularhistory.models import Model


class QuoteAttribution(Model):
    """An attribution of a quote to an entity."""

    quote = models.ForeignKey(
        'quotes.Quote', related_name='attributions', on_delete=models.CASCADE
    )
    attributee = models.ForeignKey(
        'entities.Entity', related_name='quote_attributions', on_delete=models.CASCADE
    )
    position = models.PositiveSmallIntegerField(default=0, blank=True)

    class Meta:
        """
        Meta options for QuoteAttribution.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

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
