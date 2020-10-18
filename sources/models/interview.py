"""Model classes for interviews."""

from modularhistory.utils.soup import soupify

from modularhistory.fields import ExtraField
from sources.models.spoken_source import SpokenSource

INTERVIEWERS_MAX_LENGTH: int = 200


class Interview(SpokenSource):
    """An interview (as a source)."""

    # interviewers = jsonstore.CharField(
    #     max_length=INTERVIEWERS_MAX_LENGTH,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    interviewers = ExtraField(null=True, blank=True, json_field_name='extra')

    def __str__(self) -> str:
        """TODO: write docstring."""
        return soupify(self.__html__).get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            f'{self.attributee_string} to {self.interviewers or "interviewer"}',
            self.date.string if self.date else ''
        ]
        return self.components_to_html(components)
