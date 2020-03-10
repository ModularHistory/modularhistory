from os import listdir, rename
from os.path import isfile, join
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models

from history import settings
from history.fields.file_field import SourceFileField, upload_to
from history.models import Model


class SourceFile(Model):
    file = SourceFileField(upload_to=upload_to('sources/'), null=True, blank=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    page_offset = models.SmallIntegerField(default=0, blank=True)
    first_page_number = models.SmallIntegerField(default=1, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.file_name} (page offset: {self.page_offset})'

    @property
    def file_name(self) -> Optional[str]:
        if self.file:
            return self.file.name.replace('sources/', '')
        return None

    @property
    def url(self) -> str:
        return self.file.url

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude=exclude, validate_unique=validate_unique)
        if not self.file:
            raise ValidationError('No file.')

    def save(self, *args, **kwargs):
        if self.name and self.name != self.file_name:
            full_path = f'{settings.MEDIA_ROOT}/sources'
            files = [f for f in listdir(full_path) if isfile(join(full_path, f))]
            if self.file_name in files:
                rename(f'{full_path}/{self.file_name}', f'{full_path}/{self.name}')
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
