import logging
from os import remove
from os.path import join

from django.db.models.fields.files import FieldFile

from modularhistory import settings
from modularhistory.utils import files


class TextualSourceFile(FieldFile):
    """A source file for a textual source."""

    # TODO
    @staticmethod
    def dedupe():
        """Remove duplicated source files."""
        path = join(settings.MEDIA_ROOT, 'sources')
        duplicated_files = files.get_duplicated_files(path)
        from sources.models import Source

        source_set = Source.objects.all()
        for source in source_set:
            if source.source_file:
                for duplicated_file, duplicate_files in duplicated_files.items():
                    for filename in duplicate_files:
                        logging.info(f'{filename} -> {duplicated_file}')
                        if source.source_file.name == filename:
                            logging.info(source.source_file.name)
                            remove(join(settings.MEDIA_ROOT, filename))
                            source.source_file.name = duplicated_file
                            source.save()
