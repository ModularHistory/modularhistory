"""Model classes for interviews."""

from bs4 import BeautifulSoup
from django.db import models

from history.fields import ExtraField
from sources.models.spoken_source import OldSpokenSource, SpokenSource

INTERVIEWERS_MAX_LENGTH: int = 200


class OldInterview(OldSpokenSource):
    """TODO: write docstring."""

    interviewers = models.CharField(
        max_length=INTERVIEWERS_MAX_LENGTH,
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            f'{self.attributee_string} to {self.interviewers or "interviewer"}',
            self.date.string if self.date else ''
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')


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
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            f'{self.attributee_string} to {self.interviewers or "interviewer"}',
            self.date.string if self.date else ''
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')
