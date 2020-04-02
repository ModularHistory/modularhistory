from bs4 import BeautifulSoup
from django.db import models
from django.utils.safestring import SafeText

from places.models import Venue
from .base import Source, TitleMixin


class SpokenSource(Source):
    class Meta:
        abstract = True

    @property
    def _html(self) -> str:
        raise NotImplementedError


speech_types = (
    ('address', 'address'),
    ('discourse', 'discourse'),
    ('lecture', 'lecture'),
    ('sermon', 'sermon'),
    ('speech', 'speech'),
    ('statement', 'statement'),
)


class Speech(TitleMixin, SpokenSource):
    type2 = models.CharField(max_length=10, choices=speech_types, default='speech')
    audience = models.CharField(max_length=100, null=True, blank=True)

    HISTORICAL_ITEM_TYPE = 'delivery'

    class Meta:
        verbose_name_plural = 'Speeches'

    def __str__(self):
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> str:
        string = f'{self.attributee_string}, ' if self.attributee_string else ''
        string += f'"{self.title_html}," ' if self.title else ''
        string += f'{self.type2}'
        string += ' delivered' if self.type2 not in ('statement',) else ''
        if self.audience or self.location:
            string += f' to {self.audience}' if self.audience else ''
            if self.location:
                location, location_string = self.location, self.location.string
                preposition = location.preposition if isinstance(location, Venue) else 'in'
                string += f' {preposition} {location_string}'
            string += ', '
        else:
            string += ' ' if self.date.month_is_known else ' in '
        string += self.date.string
        return string


class Interview(SpokenSource):
    HISTORICAL_ITEM_TYPE = 'interview'

    interviewers = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> str:
        string = f'{self.attributee_string} to {self.interviewers or "interviewer"}, '
        string += f'{self.date.string}' if self.date else ''
        return string


class VideoSource(Source):
    class Meta:
        abstract = True

    @property
    def _html(self) -> str:
        raise NotImplementedError


class Documentary(TitleMixin, VideoSource):
    class Meta:
        verbose_name_plural = 'Documentaries'

    def __str__(self) -> SafeText:
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> str:
        string = f'{self.attributee_string}, '
        string += f'<em>{self.title}</em>," ' if self.title else ''
        string += f'{self.date.string}' if self.date else ''
        return string
