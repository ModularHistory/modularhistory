"""Model classes for spoken sources."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.source import PolymorphicSource, Source

FILM_TYPES = (('documentary', 'Documentary'),)


class PolymorphicFilm(PolymorphicSource):
    """A video source."""

    type = models.CharField(
        verbose_name=_('film type'),
        max_length=12,
        choices=FILM_TYPES,
        default=FILM_TYPES[0][0],
    )

    def __html__(self) -> str:
        """Return the film's citation HTML string."""
        components = [
            self.attributee_html,
            f'<em>{self.linked_title}</em>',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)


class VideoSource(Source):
    """A video source."""

    def __html__(self) -> str:
        """TODO: write docstring."""
        raise NotImplementedError


class Documentary(VideoSource):
    """A documentary (as a source)."""

    class Meta:
        verbose_name_plural = 'Documentaries'

    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_html,
            f'<em>{self.linked_title}</em>',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
