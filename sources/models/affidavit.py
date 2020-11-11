"""Model classes for affidavits (as sources)."""

from django.core.exceptions import ValidationError

from modularhistory.fields import ExtraField
from sources.models.document import DocumentSource

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 100

JSON_FIELD_NAME = 'extra'


class Affidavit(DocumentSource):
    """An affidavit (as a source)."""

    certifier = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )

    class FieldNames(DocumentSource.FieldNames):
        certifier = 'certifier'

    extra_fields = {
        **DocumentSource.extra_fields,
        FieldNames.certifier: 'string',
    }
    inapplicable_fields = [
        FieldNames.publication,
    ]

    def clean(self):
        """TODO: add docstring."""
        super().clean()
        if not self.location:
            raise ValidationError('Affidavit needs a certification location.')

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_html,
            f'affidavit sworn {self.date_html} at {self.location.string} before {self.certifier}',
        ]
        return self.components_to_html(components)
