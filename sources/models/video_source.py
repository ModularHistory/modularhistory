"""Model classes for spoken sources."""

from bs4 import BeautifulSoup

from sources.models.source import OldTitledSource, Source, TypedSource


class OldVideoSource(Source):
    """TODO: write docstring."""

    class Meta:
        abstract = True

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        raise NotImplementedError


class VideoSource(TypedSource):
    """A video source."""

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        raise NotImplementedError


class OldDocumentary(OldTitledSource, OldVideoSource):
    """TODO: write docstring."""

    class Meta:
        verbose_name_plural = 'Documentaries'

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_string,
            f'<em>{self.linked_title}</em>',
            self.date.string if self.date else ''
        ]

        # Remove blank values
        components = [component for component in components if component]

        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')


class Documentary(VideoSource):
    """A documentary (as a source)."""

    class Meta:
        verbose_name_plural = 'Documentaries'

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_string,
            f'<em>{self.linked_title}</em>',
            self.date.string if self.date else ''
        ]

        # Remove blank values
        components = [component for component in components if component]

        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')
