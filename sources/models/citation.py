import re
from typing import Optional

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, CASCADE, PositiveSmallIntegerField
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
    citation_phrase = models.CharField(max_length=10, choices=citation_phrase_options,
                                       default=None, null=True, blank=True)
    source = ForeignKey(Source, related_name='citations', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    page_number = PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = PositiveSmallIntegerField(null=True, blank=True)
    position = PositiveSmallIntegerField(
        default=1, blank=True,
        help_text='Determines the order of references.'
    )

    class Meta:
        verbose_name = 'citation'
        unique_together = ['source', 'content_type', 'object_id',
                           'page_number', 'end_page_number', 'position']
        ordering = ['position', 'source', 'page_number']

    def __str__(self) -> SafeText:
        page_string = ''
        if self.page_number:
            page_string = f'p{"p" if self.end_page_number else ""}. {self.page_number}'
            if self.end_page_number:
                page_string += f'–{self.end_page_number}'
        string = f'{self.source.string}{", " if page_string else ""}{page_string}'
        if self.source.attributees.exists():
            from quotes.models import Quote
            if isinstance(self.content_object, Quote):
                quote = self.content_object
                if quote.ordered_attributees != self.source.ordered_attributees:
                    source_string = string
                    if not quote.citations.filter(position__lt=self.position).exists():
                        string = f'{quote.attributee_string}'
                        string += f', {quote.date_string}' if quote.date else ''
                        string += f', quoted in {source_string}'
                    else:
                        prior_citations = quote.citations.filter(position__lt=self.position)
                        prior_citation = prior_citations.last()
                        if 'quoted in' not in str(prior_citation):
                            string = f'quoted in {source_string}'
                        else:
                            string = f'also in {source_string}'
        return mark_safe(string)

    @property
    def html(self) -> SafeText:
        html = str(self)
        print(f'>>> {html}')
        if self.source_file_url:
            html += (
                f'<a href="{self.source_file_url}" class="display-source"'
                f' target="_blank" data-toggle="modal" data-target="#modal">'
                f'<i class="fas fa-search"></i>'
                f'</a>'
            )
        elif self.source.url or self.source.container and self.source.container.url:
            link = self.source.url if self.source.url else self.source.container.url
            if self.page_number:
                if 'www.sacred-texts.com' in link:
                    link += f'#page_{self.page_number}'
                elif 'josephsmithpapers.org' in link:
                    link += f'/{self.page_number}'
            html += (
                f'<a href="{link}" target="_blank">'
                f'<i class="fas fa-search"></i>'
                f'</a>'
            )
        return mark_safe(f'<span class="citation">{html}</span>')

    @property
    def number(self):
        return self.position + 1

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
