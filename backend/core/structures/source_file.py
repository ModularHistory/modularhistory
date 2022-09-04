import logging
from os import remove
from os.path import join
from typing import TYPE_CHECKING

from django.conf import settings
from django.db.models.fields.files import FieldFile

from core.utils import files

if TYPE_CHECKING:
    from apps.sources.models.source import Source
    from apps.sources.models.source_file import SourceFile


class TextualSourceFile(FieldFile):
    """A source file for a textual source."""

    # TODO
    def dedupe(self):
        """Remove duplicated source files."""
        path = join(settings.MEDIA_ROOT, 'sources')
        duplicated_files = files.get_duplicated_files(path)
        model_cls = self.instance.__class__
        source_file: 'SourceFile'
        for source_file in model_cls.objects.all():
            for duplicated_file, duplicate_files in duplicated_files.items():
                for filename in duplicate_files:
                    duplicated_file_name = join('sources', duplicated_file)
                    source_file_name = join('sources', filename)
                    if source_file.name == source_file_name:
                        designated_source_file: 'SourceFile' = model_cls.objects.get(
                            file=duplicated_file_name
                        )
                        logging.info(f'{source_file.name} -> {duplicated_file_name}')
                        remove(join(settings.MEDIA_ROOT, filename))
                        source: 'Source'
                        for source in source_file.sources.all():
                            source.db_file = designated_source_file
                            source.save()
                        source_file.delete()
