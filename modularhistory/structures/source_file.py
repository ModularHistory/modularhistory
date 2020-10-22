from copy import deepcopy
from os import listdir, remove
from os.path import isfile, join

from django.db.models.fields.files import FieldFile

from modularhistory import settings


class TextualSourceFile(FieldFile):
    """A source file for a textual source."""

    @staticmethod
    def dedupe():
        """Removes duplicated source files."""
        from sources.models import Source

        path = join(settings.MEDIA_ROOT, 'sources')
        files1 = [
            filename.replace('.pdf', '')
            for filename in listdir(path)
            if isfile(join(path, filename))
        ]
        files2 = deepcopy(files1)
        to_edit = []
        for filename2 in files2:
            for filename1 in files1:
                should_be_edited = all(
                    [
                        filename2 in filename1,
                        filename2 != filename1,
                        filename2.startswith(filename1[:3]),
                    ]
                )
                if should_be_edited:
                    to_edit.append(
                        (f'sources/{filename1}.pdf', f'sources/{filename2}.pdf')
                    )
        for file_a, file_b in to_edit:
            print(f'{file_a} -> {file_b}')
        source_set = Source.objects.all()
        for source in source_set:
            if source.source_file:
                for file_a, file_b in to_edit:
                    if source.source_file.name == file_a:
                        print(source.source_file.name)
                        remove(f'{settings.MEDIA_ROOT}/{file_a}')
                        source.source_file.name = file_b
                        source.save()
