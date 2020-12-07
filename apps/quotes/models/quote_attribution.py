"""Quote attributions."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from modularhistory.models.positioned_relation import PositionedRelation


class QuoteAttribution(PositionedRelation):
    """An attribution of a quote to an entity."""

    quote = models.ForeignKey(
        to='quotes.Quote',
        on_delete=models.CASCADE,
        related_name='attributions',
        verbose_name=_('quote'),
    )
    attributee = models.ForeignKey(
        to='entities.Entity',
        on_delete=models.CASCADE,
        related_name='quote_attributions',
        verbose_name=_('attributee'),
    )

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
