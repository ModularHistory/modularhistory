from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from typedmodels.models import TypedModel

from modularhistory.fields import HTMLField
from modularhistory.models import Model
from modularhistory.utils.html import soupify

PUBLICATION_TYPES = (
    ('journal', 'Journal'),
    ('newspaper', 'Newspaper'),
    ('magazine', 'Magazine'),
)


class Publication(TypedModel, Model):
    """A publication, such as a newspaper, magazine, journal, or website."""

    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    aliases = models.CharField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True, paragraphed=True)

    class Meta:
        ordering = ['name']

    searchable_fields = ['name', 'aliases']

    def __str__(self) -> str:
        """Return the publication's string representation."""
        return soupify(self.html).get_text()

    @property
    def html(self) -> SafeString:
        """Return the publication's HTML representation."""
        return format_html(self.__html__)

    @property
    def __html__(self) -> str:
        """Return the publication's HTML representation."""
        return f'<i>{self.name}</i>'


class Journal(Publication):
    """A journal that publishes articles."""

    pass  # noqa: WPS604


class Magazine(Publication):
    """A magazine that publishes articles."""

    pass  # noqa: WPS604


class Newspaper(Publication):
    """A newspaper that publishes articles."""

    pass  # noqa: WPS604
