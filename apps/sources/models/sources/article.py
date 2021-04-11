"""Model classes for articles."""

from typing import List, Optional

from django.db import models

from apps.sources.models import PolymorphicSource
from apps.sources.models.mixins.page_numbers import PageNumbersMixin


class Article(PolymorphicSource, PageNumbersMixin):
    """An article published by a journal, magazine, or newspaper."""

    publication = models.ForeignKey(to='sources.Publication', on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    volume = models.PositiveSmallIntegerField(null=True, blank=True)

    def __html__(self) -> str:
        """Return the article's citation HTML string."""
        title = self.linked_title.replace('"', "'") if self.linked_title else ''
        components: List[Optional[str]] = [
            self.attributee_html,
            f'"{title}"' if title else '',
            self.publication.html,
            f'vol. {self.volume}' if self.volume else '',
            f'no. {self.number}' if self.number else '',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
