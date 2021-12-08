"""Source containments."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import Serializer

from core.models.relations.moderated import ModeratedPositionedRelation

PHRASE_MAX_LENGTH: int = 12


class SourceContainment(ModeratedPositionedRelation):
    """A source containment."""

    class ContainmentPhrase(models.TextChoices):
        """Containment phrase options."""

        ARCHIVED = 'archived', _('archived in')
        CITED = 'cited', _('cited in')
        COPY = 'copy', _('copy in')
        INCLUDED = 'included', _('as included in')
        QUOTED = 'quoted', _('quoted in')
        RECORDED = 'recorded', _('recorded in')
        REPRODUCED = 'reproduced', _('reproduced in')
        TRANSCRIBED = 'transcribed', _('transcribed in')
        __empty__ = '-------'

    source = ForeignKey(
        to='sources.Source',
        on_delete=CASCADE,
        related_name='source_containments',
    )
    container = ForeignKey(
        to='sources.Source',
        on_delete=CASCADE,
        related_name='container_containments',
    )
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    phrase = models.CharField(
        max_length=PHRASE_MAX_LENGTH,
        choices=ContainmentPhrase.choices,
        default='',
        blank=True,
    )

    class Meta:
        ordering = ['position', 'source']

    @classmethod
    def get_serializer(self) -> Serializer:
        """Return the serializer for the entity."""
        from apps.sources.api.serializers import SourceContainmentSerializer

        return SourceContainmentSerializer

    def __str__(self) -> str:
        """Return the containment's string representation."""
        return format_html(f'{self.phrase} in {self.container}')

    def clean(self):
        """Prepare the containment to be saved."""
        super().clean()
        if self.source in self.container.containers.all():
            raise ValidationError(
                f'{self.source} cannot be contained by {self.container}; '
                f'the latter is already contained by the former.'
            )
