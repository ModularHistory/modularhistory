"""Model classes for correspondence (as sources)."""

from modularhistory.utils.soup import soupify

from modularhistory.fields import ExtraField
from sources.models.document import DocumentSource

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 100


CORRESPONDENCE_TYPES = (
    ('email', 'email'),
    ('letter', 'letter'),
    ('memorandum', 'memorandum'),
)
TYPE_MAX_LENGTH: int = 10


class Correspondence(DocumentSource):
    """Correspondence (as a source)."""

    # recipient = jsonstore.CharField(
    #     max_length=NAME_MAX_LENGTH,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    type_label = 'correspondence'

    def __str__(self) -> str:
        """TODO: write docstring."""
        return soupify(self.__html__).get_text()

    recipient = ExtraField(json_field_name='extra')

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        html = f'{self.attributee_string}, '
        if self.href:
            html = f'{html}<a href="{self.href}" target="_blank">'
        html = f'{html}{self.type_label} to {self.recipient or "<Unknown>"}'
        if self.date:
            html += ', dated ' if self.date.day_is_known else ', '
            html += self.date.string
        if self.href:
            html = f'{html}</a>'
        if self.descriptive_phrase:
            html = f'{html}, {self.descriptive_phrase}'
        if self.collection:
            html = f'{html}, archived in {self.collection}'
        return html


class Email(Correspondence):
    """An email (as a source)."""

    type_label = 'email'


class Letter(Correspondence):
    """A letter (as a source)."""

    type_label = 'letter'


class Memorandum(Correspondence):
    """A memorandum (as a source)."""

    type_label = 'memorandum'
