"""Model classes for spoken sources."""

from bs4 import BeautifulSoup

from modularhistory.fields import ExtraField
from places.models import Venue
from sources.models.source import Source


class SpokenSource(Source):
    """Spoken words (e.g., a speech, lecture, or discourse) as a source."""

    # audience = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    audience = ExtraField(json_field_name='extra')

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        type_label = str(self.type_label)
        delivery_string = f'{type_label}'
        audience, location, date = self.audience, self.location, self.date
        if any([audience, location, date]):
            if type_label != 'statement':
                delivery_string = f'{type_label} delivered'
            if audience or location:
                if audience:
                    delivery_string = f'{delivery_string} to {audience}'
                if location:
                    preposition = location.preposition if isinstance(location, Venue) else 'in'
                    delivery_string = f'{delivery_string} {preposition} {location.string}'
                if date:
                    delivery_string = f'{delivery_string}, {self.date_string}'
            elif date:
                if date.month_is_known:
                    delivery_string = f'{delivery_string} {self.date_string}'
                else:
                    delivery_string = f'{delivery_string} in {self.date_string}'
        # Build full string
        components = [
            self.attributee_string,
            f'"{self.linked_title}"' if self.title else '',
            delivery_string
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')

    @property
    def type_label(self) -> str:
        """Type label used in strings; e.g., 'speech', 'discourse', 'lecture', etc."""
        raise NotImplementedError


class Speech(SpokenSource):
    """A speech as a source."""

    type_label = 'speech'

    class Meta:
        verbose_name_plural = 'Speeches'


class Address(SpokenSource):
    """An address as a source."""

    type_label = 'address'

    class Meta:
        verbose_name_plural = 'Addresses'


class Discourse(SpokenSource):
    """A discourse as a source."""

    type_label = 'discourse'

    class Meta:
        verbose_name_plural = 'Discourses'


class Lecture(SpokenSource):
    """A lecture as a source."""

    type_label = 'lecture'

    class Meta:
        verbose_name_plural = 'Lectures'


class Sermon(SpokenSource):
    """A sermon as a source."""

    type_label = 'sermon'

    class Meta:
        verbose_name_plural = 'Sermons'


class Statement(SpokenSource):
    """A statement as a source."""

    type_label = 'statement'

    class Meta:
        verbose_name_plural = 'Statements'
