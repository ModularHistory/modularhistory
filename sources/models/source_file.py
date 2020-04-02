from os import listdir, rename
from os.path import isfile, join
from typing import Optional
from django.utils.safestring import SafeText, mark_safe

from django.core.exceptions import ValidationError
from django.db import models

from history import settings
from history.fields.file_field import SourceFileField, upload_to
from history.models import Model


class SourceFile(Model):
    file = SourceFileField(upload_to=upload_to('sources/'), null=True, blank=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    page_offset = models.SmallIntegerField(
        default=0, blank=True,
        help_text='The difference between the page numbers displayed on the pages '
                  'and the actual page numbers of the electronic file (a positive '
                  'number if the electronic page number is greater than the textual'
                  'page number; a negative number if the textual page number is '
                  'greater than the electronic page number).'
    )
    first_page_number = models.SmallIntegerField(
        default=1, blank=True,
        help_text='The page number that is visibly displayed on the page '
                  'on which the relevant text begins (usually 1).'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.file_name} (page offset: {self.page_offset})'

    @property
    def default_page_number(self):
        """Page number to be opened by default for the source file."""
        return self.first_page_number + self.page_offset

    @property
    def file_name(self) -> Optional[str]:
        if self.file:
            return self.file.name.replace('sources/', '')
        return None

    @property
    def link(self) -> Optional[SafeText]:
        return mark_safe(f'<a href="{self.url}" class="display-source" target="_blank">'
                         f'<i class="fa fa-search"></i></a>')

    @property
    def url(self) -> str:
        url = self.file.url
        if url.endswith('epub'):
            url = f'/history/sources/epub{url}'
        return url

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude=exclude, validate_unique=validate_unique)
        if not self.file:
            raise ValidationError('No file.')

    def save(self, *args, **kwargs):
        if self.name and self.name != self.file_name:
            full_path = join(settings.MEDIA_ROOT, 'sources')
            files = [f for f in listdir(full_path) if isfile(join(full_path, f))]
            if self.file_name in files:
                rename(join(full_path, self.file_name), join(full_path, self.name))
                self.file.name = f'sources/{self.name}'
        if 'sources/sources' in self.file.name:
            raise ValidationError(f'Bad file name: {self.file.name}')
        if self.file.name.endswith('None'):
            raise ValidationError(f'Bad file name: {self.file.name}')
        super().save(*args, **kwargs)
        # Set the name attr after the initial save,
        # because the initial save modifies the file name.
        if not self.name:
            self.name = self.file_name
            super().save()
