"""Model classes for source files."""

import logging
from datetime import datetime
from os.path import join
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.files.storage import Storage, default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.moderation.models import ModeratedModel
from core.fields.file_field import SourceFileField, upload_to
from core.models.model import ExtendedModel
from core.templatetags.media import media as fix_url


class SourceFile(ModeratedModel):
    """A source file with page numbers."""

    file = SourceFileField(
        upload_to=upload_to('sources/'),
        null=True,
        blank=True,
        unique=True,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
    )
    page_offset = models.SmallIntegerField(
        default=0,
        blank=True,
        help_text=(
            'The difference between the page numbers displayed on the pages '
            'and the actual page numbers of the electronic file (a positive '
            'number if the electronic page number is greater than the textual'
            'page number; a negative number if the textual page number is '
            'greater than the electronic page number).'
        ),
    )
    first_page_number = models.SmallIntegerField(
        default=1,
        blank=True,
        help_text=(
            'The page number that is visibly displayed on the page '
            'on which the relevant text begins (usually 1).'
        ),
    )
    uploaded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        """Return the source file's string representation."""
        return f'{self.file_name} (page offset: {self.page_offset})'

    def save(self, *args, **kwargs):
        """Save the source file to the database."""
        self.clean()
        storage: Storage = default_storage
        if isinstance(getattr(self.file, 'file', None), UploadedFile):
            # If a file was just uploaded...
            self.uploaded_at = datetime.now()  # TODO: timezone
        elif not self.uploaded_at:
            try:
                self.uploaded_at = storage.get_created_time(self.file.name)
            except Exception as err:
                logging.error(f'{err}')
        if self.name and self.name != self.file_name:
            if storage.exists(self.file.name):
                old_name = self.file.name
                new_name = join('sources', self.name)
                logging.debug(f'Renaming {old_name} to {new_name}...')
                source_file = storage.open(old_name)
                storage.save(new_name, source_file)
                self.file.name = new_name
                storage.delete(old_name)
            else:
                logging.debug(f'{self.file.name} does not exist in {storage}.')
        elif not self.name:
            self.name = storage.get_available_name(self.file.name)
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Prepare the source file to be saved."""
        super().clean()
        if self.file:
            bad_filename_conditions = (
                self.file.name.endswith('None'),
                'sources/sources' in self.file.name,
            )
            if any(bad_filename_conditions):
                raise ValidationError(f'Bad file name: {self.file.name}')
        else:
            raise ValidationError('No file is selected.')

    @property
    def default_page_number(self):
        """Page number to be opened by default for the source file."""
        return self.first_page_number + self.page_offset

    @property
    def file_name(self) -> Optional[str]:
        """Return the filename with the path stripped."""
        if self.file:
            return self.file.name.replace('sources/', '')
        return None

    @property
    def link(self) -> Optional[SafeString]:
        """Return a link for viewing the source file."""
        return format_html(
            f'<a href="{self.url}" class="display-source" target="_blank">'
            f'<i class="fa fa-search"></i></a>'
        )

    @property
    def url(self) -> str:
        """Return the URL of the source file."""
        url = self.file.url
        if url.endswith('epub'):
            url = f'/sources/epub{url}'
        return fix_url(url)
