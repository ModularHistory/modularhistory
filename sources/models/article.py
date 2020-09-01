# type: ignore
# TODO: remove above line after fixing typechecking
from bs4 import BeautifulSoup
from django.db import models
from django.db.models import ForeignKey, CASCADE
from django.utils.safestring import SafeText, mark_safe

from history.fields import HTMLField
from history.models import Model
from .base import TextualSource, TitleMixin
from .piece import _Piece

publication_types = (
    ('journal', 'Journal'),
    ('newspaper', 'Newspaper'),
    ('magazine', 'Magazine'),
)


class Publication(Model):
    type2 = models.CharField(max_length=10, null=True, blank=True, choices=publication_types)
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    aliases = models.CharField(max_length=100, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    searchable_fields = ['name', 'aliases']

    def __str__(self) -> SafeText:
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> SafeText:
        return mark_safe(f'<i>{self.name}</i>')

    @property
    def html(self) -> SafeText:
        return mark_safe(self._html)


class Article(TitleMixin, _Piece):
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    volume = models.PositiveSmallIntegerField(null=True, blank=True)
    publication = ForeignKey(Publication, null=True, blank=True, on_delete=CASCADE)

    searchable_fields = ['db_string', 'publication__name']

    def __str__(self) -> SafeText:
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> SafeText:
        string = f'{self.attributee_string}, ' if self.pk and self.attributee_string else ''
        title_html = self.title_html.replace('"', "'") if self.title else None
        string += f'"{title_html}," ' if self.title else ''
        string += f'{self.publication.html}' if self.publication else ''  # TODO: make required
        string += f', vol. {self.volume}' if self.volume else ''
        string += f', no. {self.number}' if self.number else ''
        string += f', {self.date.string}' if self.date else ''
        return mark_safe(string)


class WebPage(TitleMixin, TextualSource):
    website_title = models.CharField(max_length=100, null=True, blank=True)
    organization_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> SafeText:
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> SafeText:
        string = f'{self.attributee_string}, ' if self.attributee_string else ''
        string += f'"{self.title_html}," ' if self.title else ''
        string += f'<i>{self.website_title}</i>'
        string += f', {self.organization_name}' if self.organization_name else ''
        string += f', {self.date.string}' if self.date else ''
        string += f', retrieved from <a target="_blank" href="{self.url}">{self.url}</a>'
        return mark_safe(string)
