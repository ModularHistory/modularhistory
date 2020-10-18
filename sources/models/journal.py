"""Model classes for journals (as sources)."""

from modularhistory.utils.soup import soupify

from sources.models.piece import SourceWithPageNumbers

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 100


class JournalEntry(SourceWithPageNumbers):
    """A journal entry (as a source)."""

    class Meta:
        verbose_name_plural = 'Journal entries'

    def __str__(self) -> str:
        """TODO: add docstring."""
        return soupify(self.__html__).get_text()

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_string,
            f'{"journal" if self.attributee_string else "Journal"} entry dated {self.date.string}'
        ]
        return self.components_to_html(components)
