"""Source containments."""

from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.utils.html import format_html

from apps.sources.serializers import ContainmentSerializer
from modularhistory.models.positioned_relation import PositionedRelation

PHRASE_MAX_LENGTH: int = 12
CONTAINMENT_PHRASES = (
    ('', '-----'),
    ('archived', 'archived'),
    ('cited', 'cited'),
    ('copy', 'copy'),
    ('quoted', 'quoted'),
    ('recorded', 'recorded'),
    ('reproduced', 'reproduced'),
    ('transcribed', 'transcribed'),
)


class SourceContainment(PositionedRelation):
    """A source containment."""

    source = ForeignKey(
        to='sources.PolymorphicSource',
        on_delete=CASCADE,
        related_name='source_containments',
    )
    container = ForeignKey(
        to='sources.PolymorphicSource',
        on_delete=CASCADE,
        related_name='container_containments',
    )
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    phrase = models.CharField(
        max_length=PHRASE_MAX_LENGTH,
        choices=CONTAINMENT_PHRASES,
        default='',
        blank=True,
    )

    class Meta:
        ordering = ['position', 'source']

    serializer = ContainmentSerializer

    def __str__(self) -> str:
        """TODO: write docstring."""
        return format_html(f'{self.phrase} in {self.container}')
