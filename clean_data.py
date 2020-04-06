
import os
import sys

import django

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()


# from history import settings
# from django.db import transaction
# from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from sources.models import Citation, QSR, OSR

occurrence = ContentType.objects.get(app_label='occurrences', model='occurrence')
quote = ContentType.objects.get(app_label='quotes', model='quote')

qsrs = QSR.objects.using('backup').all()
osrs = OSR.objects.using('backup').all()

for qsr in qsrs:
    c = Citation.objects.get_or_create(
        citation_phrase=qsr.citation_phrase,
        source=qsr.source,
        content_type=quote,
        object_id=qsr.quote.id,
        content_object=qsr.quote,
        page_number=qsr.page_number,
        end_page_number=qsr.end_page_number,
        position=qsr.position
    )
    print(f'>>> {c}')

for osr in osrs:
    c = Citation.objects.get_or_create(
        citation_phrase=osr.citation_phrase,
        source=osr.source,
        content_type=occurrence,
        object_id=osr.occurrence.id,
        content_object=osr.occurrence,
        page_number=osr.page_number,
        end_page_number=osr.end_page_number,
        position=osr.position
    )
    print(f'>>> {c}')
