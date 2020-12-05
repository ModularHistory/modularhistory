"""Model classes for journals (as sources)."""

from .piece import SourceWithPageNumbers

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 100


class JournalEntry(SourceWithPageNumbers):
    """A journal entry (as a source)."""

    class Meta:
        """
        Meta options for the JournalEntry model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """
        verbose_name_plural = 'Journal entries'

    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_html,
            f'{"journal" if self.attributee_html else "Journal"} entry dated {self.date.string}',
        ]
        return self.components_to_html(components)
