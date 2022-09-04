"""Model classes for journals (as sources)."""

from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.source import Source


class Entry(Source, PageNumbersMixin):
    """A journal entry."""

    class Meta:
        """Meta options for the Entry model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
        verbose_name_plural = 'journal entries'

    def __html__(self) -> str:
        """Return the citation HTML string for the journal entry."""
        components = [
            self.attributee_html,
            f'{"journal" if self.attributee_html else "Journal"} entry dated {self.date.string}',
        ]
        return self.components_to_html(components)
