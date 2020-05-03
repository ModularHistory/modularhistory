import os
import sys
from glob import glob

import django
from decouple import config
from django.core import management
from paramiko import SSHClient
from scp import SCPClient

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()

from history import settings


from history import settings
from django.db import transaction
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from sources.models import Citation, Source, PageRange
from occurrences.models import Occurrence
from quotes.models import QuoteRelation, Quote
from topics.models import Topic, TopicRelation

occurrence_ct = ContentType.objects.get_for_model(Occurrence)
quote_ct = ContentType.objects.get_for_model(Quote)


for citation in Citation.objects.all():
    if citation.page_number:
        pr = PageRange()
        pr.citation = citation
        pr.page_number = citation.page_number
        if citation.end_page_number:
            pr.end_page_number = citation.end_page_number
        try:
            pr.save()
            print(f'>>> {pr}')
        except Exception as e:
            print(f'>>> {e}')
