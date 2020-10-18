"""Model classes for affidavits (as sources)."""

from modularhistory.utils.soup import soupify
from django.core.exceptions import ValidationError

from modularhistory.fields import ExtraField
from sources.models.document import DocumentSource

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 100


class Affidavit(DocumentSource):
    """An affidavit (as a source)."""

    # certifier = jsonstore.CharField(
    #     max_length=NAME_MAX_LENGTH,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    certifier = ExtraField(json_field_name='extra')

    def __str__(self) -> str:
        """TODO: write docstring."""
        return soupify(self.__html__).get_text()

    def clean(self):
        """TODO: add docstring."""
        super().clean()
        if not self.location:
            raise ValidationError('Affidavit needs a certification location.')

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        components = [
            self.attributee_string,
            f'affidavit sworn {self.date_html} at {self.location.string} before {self.certifier}'
        ]
        return self.components_to_html(components)
