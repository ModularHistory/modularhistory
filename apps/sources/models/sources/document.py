"""Model classes for documents (as sources)."""

from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.sources.models import PolymorphicSource
from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from modularhistory.models import ModelWithComputations, retrieve_or_compute
from modularhistory.utils.html import soupify

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 200


class DocumentMixin(PageNumbersMixin):
    """A historical document (as a source)."""

    collection = models.ForeignKey(
        to='sources.Collection',
        related_name='%(class)s',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    collection_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='aka acquisition number',
    )
    location_info = models.TextField(
        null=True,
        blank=True,
        help_text=(
            'Ex: John Alexander Papers, Series 1: Correspondence, 1831-1848, Folder 1'
        ),
    )
    descriptive_phrase = models.CharField(
        max_length=DESCRIPTIVE_PHRASE_MAX_LENGTH,
        null=True,
        blank=True,
        help_text='e.g., "on such-and-such letterhead" or "signed by so-and-so"',
    )
    information_url = models.CharField(
        max_length=URL_MAX_LENGTH,
        null=True,
        blank=True,
        help_text='URL for information regarding the document',
    )

    class Meta:
        """Meta options for the _Engagement model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        abstract = True


class Document(PolymorphicSource, DocumentMixin):
    """A historical or contemporary document held in a collection."""

    def __html__(self) -> str:
        """Return the repository's HTML representation."""
        components = [
            self.attributee_html,
            self.linked_title if self.title else 'untitled document',
            self.date.string if self.date else 'date unknown',
            self.descriptive_phrase,
            f'archived in {self.collection}' if self.collection else '',
        ]
        return self.components_to_html(components)


class Collection(ModelWithComputations):
    """A collection of documents."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='e.g., "Adam S. Bennion papers"',
        null=True,
        blank=True,
    )
    repository = ForeignKey(
        'sources.Repository',
        on_delete=CASCADE,
        help_text='the library or institution housing the collection',
    )
    url = models.URLField(max_length=URL_MAX_LENGTH, null=True, blank=True)

    class Meta:
        unique_together = ['name', 'repository']

    def __str__(self) -> str:
        """Return the collection's string representation."""
        return soupify(self.html).get_text()

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='html', caster=format_html)
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


class Repository(ModelWithComputations):
    """A repository of collections of documents."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        null=True,
        blank=True,
        help_text='e.g., "L. Tom Perry Special Collections"',
    )
    owner = models.CharField(
        max_length=NAME_MAX_LENGTH,
        null=True,
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
    @retrieve_or_compute(attribute_name='html', caster=format_html)
    def html(self) -> SafeString:
        """Return the collection's HTML representation."""
        return format_html(self.__html__())

    def __html__(self) -> str:
        """Return the repository's HTML representation."""
        location_string = self.location.string if self.location else None
        components = [self.name, self.owner, location_string]
        return ', '.join([component for component in components if component])
