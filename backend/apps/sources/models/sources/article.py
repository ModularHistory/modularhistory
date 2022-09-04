"""Model classes for articles."""

from typing import Optional

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.source import Source


class Article(Source, PageNumbersMixin):
    """An article published by a journal, magazine, or newspaper."""

    publication = models.ForeignKey(
        to='sources.Publication',
        on_delete=models.PROTECT,
        verbose_name=_('publication'),
    )
    number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('number'),
    )
    volume = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('volume'),
    )

    def __html__(self) -> str:
        """Return the article's citation HTML string."""
        title = self.linked_title.replace('"', "'") if self.linked_title else ''
        components: list[Optional[str]] = [
            self.attributee_html,
            f'"{title}"' if title else '',
            self.publication.html,
            f'vol. {self.volume}' if self.volume else '',
            f'no. {self.number}' if self.number else '',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
