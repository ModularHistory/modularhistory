"""Model classes for articles."""

from typing import List

from bs4 import BeautifulSoup
from django.db import models
from django.db.models import CASCADE, ForeignKey

from history.fields import ExtraField
from sources.models.piece import OldSourceWithPageNumbers, SourceWithPageNumbers
from sources.models.source import OldTitledSource


class Article(SourceWithPageNumbers):
    """A published article (as a source)."""

    # Moved to base class
    # publication = ForeignKey(
    #     'sources.Publication',
    #     null=True,
    #     blank=True,
    #     on_delete=CASCADE
    # )

    # JSON fields
    # number = jsonstore.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    number = ExtraField(json_field_name='extra')

    # volume = jsonstore.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    volume = ExtraField(json_field_name='extra')

    searchable_fields = ['db_string', 'publication__name']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """
        Return the article's HTML string representation.

        The string has the following form:
            ... TODO
        """
        attributee_html = self.attributee_string
        title = self.linked_title.replace('"', "'") if self.title else ''
        publication_html = self.publication.html if self.publication else ''  # TODO: make required
        volume = f'vol. {self.volume}' if self.volume else ''
        number = f'no. {self.number}' if self.number else ''
        date = self.date.string if self.date else ''
        components: List[str] = [
            attributee_html,
            f'"{title}"' if title else '',
            publication_html,
            volume,
            number,
            date
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')


class OldArticle(OldTitledSource, OldSourceWithPageNumbers):
    """TODO: write docstring."""

    number = models.PositiveSmallIntegerField(null=True, blank=True)
    volume = models.PositiveSmallIntegerField(null=True, blank=True)
    publication = ForeignKey(
        'sources.Publication',
        null=True,
        blank=True,
        on_delete=CASCADE
    )

    searchable_fields = ['db_string', 'publication__name']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """
        Return the article's HTML string representation.

        The string has the following form:
            ... TODO
        """
        attributee_html = self.attributee_string
        title = self.linked_title.replace('"', "'") if self.title else ''
        publication_html = self.publication.html if self.publication else ''  # TODO: make required
        volume = f'vol. {self.volume}' if self.volume else ''
        number = f'no. {self.number}' if self.number else ''
        date = self.date.string if self.date else ''
        components: List[str] = [
            attributee_html,
            f'"{title}"' if title else '',
            publication_html,
            volume,
            number,
            date
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')
