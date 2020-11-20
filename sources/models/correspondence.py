"""Model classes for correspondence (as sources)."""

from modularhistory.fields import ExtraField
from sources.models.document import DocumentSource

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 100

JSON_FIELD_NAME = 'extra'

CORRESPONDENCE_TYPES = (
    ('email', 'email'),
    ('letter', 'letter'),
    ('memorandum', 'memorandum'),
)
TYPE_MAX_LENGTH: int = 10


class Correspondence(DocumentSource):
    """Correspondence (as a source)."""

    type_label = 'correspondence'

    recipient = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )

    class FieldNames(DocumentSource.FieldNames):
        recipient = 'recipient'

    extra_field_schema = {
        **DocumentSource.extra_field_schema,
        FieldNames.recipient: 'string',
    }
    inapplicable_fields = [
        FieldNames.publication,
    ]

    def __html__(self) -> str:
        """TODO: write docstring."""
        html = f'{self.attributee_html}, '
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
