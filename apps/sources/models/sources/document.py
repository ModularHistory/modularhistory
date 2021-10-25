"""Model classes for documents (as sources)."""

from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.moderation.models import ModeratedModel
from apps.sources.models.mixins.document import DocumentMixin
from apps.sources.models.source import Source
from core.models.model_with_cache import ModelWithCache, store
from core.utils.html import soupify

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 200


class Document(Source, DocumentMixin):
    """A historical or contemporary document held in a collection."""

    date_nullable = True

    def __html__(self) -> str:
        """Return the repository's HTML representation."""
        components = [
            self.attributee_html,
            self.linked_title if self.title else 'untitled document',
            self.date.string if self.date else '',
            self.descriptive_phrase,
            f'archived in {self.collection}' if self.collection else '',
        ]
        return self.components_to_html(components)


class Collection(ModeratedModel, ModelWithCache):
    """A collection of documents."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='e.g., "Adam S. Bennion papers"',
        blank=True,
    )
    repository = ForeignKey(
        to='sources.Repository',
        on_delete=CASCADE,
        help_text='the library or institution housing the collection',
    )
    url = models.URLField(
        max_length=URL_MAX_LENGTH,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ['name', 'repository']

    def __str__(self) -> str:
        """Return the collection's string representation."""
        return soupify(self.html).get_text()

    @property  # type: ignore
    @store(key='html', caster=format_html)
    def html(self) -> SafeString:
        """Return the collection's HTML representation."""
        return format_html(self.__html__())

    def __html__(self) -> str:
        """Return the collection's HTML representation."""
        components = [
            f'{self.name}' if self.name else '',
            f'{self.repository}',
        ]
        return ', '.join([component for component in components if component])


class Repository(ModeratedModel, ModelWithCache):
    """A repository of collections of documents."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        blank=True,
        help_text='e.g., "L. Tom Perry Special Collections"',
    )
    owner = models.CharField(
        max_length=NAME_MAX_LENGTH,
        blank=True,
        help_text='e.g., "Harold B. Lee Library, Brigham Young University"',
    )
    location = ForeignKey(
        'places.Place',
        on_delete=models.SET_NULL,
        related_name='repositories',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'Repositories'

    def __str__(self) -> str:
        """Return the repository's string representation."""
        return soupify(self.html).get_text()

    @property  # type: ignore
    @store(key='html', caster=format_html)
    def html(self) -> SafeString:
        """Return the collection's HTML representation."""
        return format_html(self.__html__())

    def __html__(self) -> str:
        """Return the repository's HTML representation."""
        location_string = self.location.string if self.location else None
        components = [self.name, self.owner, location_string]
        return ', '.join([component for component in components if component])
