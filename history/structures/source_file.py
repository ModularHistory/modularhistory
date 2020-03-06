from copy import deepcopy
from os import listdir, remove
from os.path import isfile, join

from django.db.models.fields.files import FieldFile

from history import settings


class TextualSourceFile(FieldFile):

    @staticmethod
    def dedupe():
        from sources.models import Source
        path = f'{settings.MEDIA_ROOT}/sources'
        files = [f.replace('.pdf', '') for f in listdir(path) if isfile(join(path, f))]
        files2 = deepcopy(files)
        to_edit = []
        for file in files2:
            for f in files:
                if file in f and file != f and file.startswith(f[:3]):
                    to_edit.append((f'sources/{f}.pdf', f'sources/{file}.pdf'))
        for a, b in to_edit:
            print(f'{a} -> {b}')
        source_set = Source.objects.all()
        for source in source_set:
            if source.file:
                for a, b in to_edit:
                    if source.file.name == a:
                        print(source.file.name)
                        remove(f'{settings.MEDIA_ROOT}/{a}')
                        source.file.name = b
                        source.save()
