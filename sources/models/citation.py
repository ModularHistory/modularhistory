import re
from typing import Optional

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, CASCADE
from django.utils.safestring import SafeText, mark_safe

from history.models import Model
from sources.models import Source

source_types = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
    ('T', 'Tertiary')
)

citation_phrase_options = (
    (None, ''),
    ('quoted in', 'quoted in'),
    ('cited in', 'cited in')
)


class Citation(Model):
    """A reference to a source (from any other model)."""
    source = ForeignKey(Source, related_name='citation_set', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    position = models.PositiveSmallIntegerField(verbose_name='reference position', default=1, blank=True)
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    citation_phrase = models.CharField(max_length=10, choices=citation_phrase_options,
                                       default=None, null=True, blank=True)

    class Meta:
        verbose_name = 'citation'
        unique_together = ['source', 'content_type', 'object_id', 'page_number', 'end_page_number', 'position']
        ordering = ['source', 'page_number']

    def __str__(self) -> SafeText:
        page_string = ''
        if self.page_number:
            page_string = f'p{"p" if self.end_page_number else ""}. {self.page_number}'
            if self.end_page_number:
                page_string += f'–{self.end_page_number}'
        string = f'{self.source.string}{", " if page_string else ""}{page_string}'
        if self.source.attributees.exists():
            if hasattr(self.content_object, 'attributee'):
                if self.content_object.attributee != self.source.attributees.first():
                    source_string = string
                    string = f'{self.content_object.attributee}'
                    if hasattr(self.content_object, 'date'):
                        string += f', {self.content_object.date_string}' if self.content_object.date else ''
                    string += f', quoted in {source_string}'
        return mark_safe(string)

    @property
    def html(self) -> SafeText:
        html = str(self)
        if self.source_file_url:
            html += (
                f'<a href="{self.source_file_url}" class="display-source"'
                f' target="_blank" data-toggle="modal" data-target="#modal">'
                f'<i class="fas fa-search"></i>'
                f'</a>'
            )
        elif self.source.link or self.source.container and self.source.container.link:
            link = self.source.link if self.source.link else self.source.container.link
            if self.page_number and 'www.sacred-texts.com' in link:
                link += f'#page_{self.page_number}'
            html += (
                f'<a href="{link}" target="_blank">'
                f'<i class="fas fa-search"></i>'
                f'</a>'
            )
        return mark_safe(f'<span class="citation">{html}</span>')

    @property
    def source_file_page_number(self) -> Optional[int]:
        file = self.source.get_file()
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
            elif hasattr(self.source, 'file_page_number'):
                return self.source.file_page_number
        return None

    @property
    def source_file_url(self) -> Optional[str]:
        file_url = self.source.file_url
        if file_url and self.source_file_page_number:
            if 'page=' in file_url:
                file_url = re.sub(r'page=\d+', f'page={self.source_file_page_number}', file_url)
            else:
                file_url = file_url + f'#page={self.source_file_page_number}'
        return file_url

    def clean(self):
        if self.end_page_number and self.end_page_number < self.page_number:
            raise ValidationError('The end page number must be greater than the start page number.')
