from django.db import models
from django.utils.safestring import SafeText, mark_safe

from places.models import Venue
from .base import Source, TitleMixin


class SpokenSource(Source):

    class Meta:
        abstract = True


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
        string = f'{self.creators}, ' if self.creators else ''
        string += f'"{self.title}," ' if self.title else ''
        string += f'{self.type2}'
        string += ' delivered' if self.type2 not in ('statement',) else ''
        if self.audience or self.location:
            string += f' to {self.audience}' if self.audience else ''
            if self.location:
                location = self.location
                preposition = location.preposition if isinstance(location, Venue) else 'in'
                string += f' {preposition} {location}'
            string += ', '
        else:
            string += ' ' if self.date.month_is_known else ' in '
        string += self.date.string
        return string


class Interview(SpokenSource):
    HISTORICAL_ITEM_TYPE = 'interview'

    interviewers = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        string = f'{self.creators} to {self.interviewers or "interviewer"}, '
        string += f'{self.date.string}' if self.date else ''
        return mark_safe(string)


class VideoSource(Source):
    class Meta:
        abstract = True


class Documentary(TitleMixin, VideoSource):
    def __str__(self) -> SafeText:
        string = f'{self.creators}, '
        string += f'<em>{self.title}</em>," ' if self.title else ''
        string += f'{self.date.string}' if self.date else ''
        return mark_safe(string)

    class Meta:
        verbose_name_plural = 'Documentaries'
