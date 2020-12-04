from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.utils.translation import ugettext_lazy as _

from modularhistory.models import Model


class SourceAttribution(Model):
    """An entity (e.g., a writer or organization) to which a source is attributed."""

    source = ForeignKey(
        to='sources.Source',
        on_delete=CASCADE,
        related_name='attributions',
        null=True,
        verbose_name=_('source'),
    )
    attributee = ForeignKey(
        to='entities.Entity', on_delete=CASCADE, related_name='source_attributions'
    )
    position = models.PositiveSmallIntegerField(
        null=True, blank=True
    )  # TODO: add cleaning logic

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.attributee.unabbreviated_name or f'{self.attributee}'
