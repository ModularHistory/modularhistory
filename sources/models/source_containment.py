"""Source containments."""

from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.utils.html import format_html

from modularhistory.models import Model

PHRASE_MAX_LENGTH: int = 12
CONTAINMENT_PHRASES = (
    ('', '-----'),
    ('archived', 'archived'),
    ('cited', 'cited'),
    ('copy', 'copy'),
    ('quoted', 'quoted'),
    ('recorded', 'recorded'),
    ('reproduced', 'reproduced'),
    ('transcribed', 'transcribed')
)


class SourceContainment(Model):
    """A source containment."""

    source = ForeignKey(
        'sources.Source',
        on_delete=CASCADE,
        related_name='source_containments',
        null=True
    )
    container = ForeignKey(
        'sources.Source',
        on_delete=CASCADE,
        related_name='container_containments',
        null=True
    )
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)  # TODO: add cleaning logic
    phrase = models.CharField(
        max_length=PHRASE_MAX_LENGTH,
        choices=CONTAINMENT_PHRASES,
        default='',
        blank=True
    )

    class Meta:
        ordering = ['position', 'source']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return format_html(f'{self.phrase} in {self.container}')
