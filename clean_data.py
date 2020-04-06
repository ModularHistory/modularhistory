
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
# from django.contrib.contenttypes.models import ContentType
from sources.models import Citation, QSR, OSR

qsrs = QSR.objects.using('backup').all()
osrs = OSR.objects.using('backup').all()

for qsr in qsrs:
    print(f'>>> {qsr}')
    # Citation.objects.create(
    #     citation_phrase=c.citation_phrase,
    #     source=c.source,
    #     content_type=c.content_type,
    #     object_id=c.object_id,
    #     content_object=c.content_object,
    #     page_number=c.page_number,
    #     end_page_number=c.end_page_number,
    #     position=c.position
    # )

for osr in osrs:
    print(f'>>> {osr}')
    # Citation.objects.create(
    #     citation_phrase=c.citation_phrase,
    #     source=c.source,
    #     content_type=c.content_type,
    #     object_id=c.object_id,
    #     content_object=c.content_object,
    #     page_number=c.page_number,
    #     end_page_number=c.end_page_number,
    #     position=c.position
    # )
