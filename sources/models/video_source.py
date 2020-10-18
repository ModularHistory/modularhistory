"""Model classes for spoken sources."""

from modularhistory.utils.soup import soupify

from sources.models.source import Source


class VideoSource(Source):
    """A video source."""

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        raise NotImplementedError


class Documentary(VideoSource):
    """A documentary (as a source)."""

    class Meta:
        verbose_name_plural = 'Documentaries'

    def __str__(self) -> str:
        """TODO: write docstring."""
        return soupify(self.__html__).get_text()

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_string,
            f'<em>{self.linked_title}</em>',
            self.date.string if self.date else ''
        ]
        return self.components_to_html(components)
