"""Model classes for affidavits (as sources)."""

from django.core.exceptions import ValidationError

from modularhistory.fields import ExtraField

from .document import DocumentSource

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

    extra_field_schema = {
        **DocumentSource.extra_field_schema,
        FieldNames.certifier: 'string',
    }
    inapplicable_fields = [
        FieldNames.publication,
    ]

    def clean(self):
        """Prepare the source to be saved."""
        super().clean()
        if not self.location:
            raise ValidationError('Affidavit needs a certification location.')

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        if self.location:
            affidavit_string = (
                f'affidavit sworn {self.date_html} at {self.location.string} '
                f'before {self.certifier}'
            )
        else:
            affidavit_string = (
                f'affidavit sworn {self.date_html} before {self.certifier}'
            )
        components = [
            self.attributee_html,
            affidavit_string,
        ]
        return self.components_to_html(components)
