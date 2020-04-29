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
from sources.models import Citation, Source
from quotes.models import QuoteRelation
from topics.models import TopicQuoteRelation, Topic


topic_ct = ContentType.objects.get_for_model(Topic)

for _oqr in TopicQuoteRelation.objects.all():
    oqr: TopicQuoteRelation = _oqr
    QuoteRelation.objects.get_or_create(
            quote=oqr.quote, object_id=oqr.topic_id,
            content_type=topic_ct
    )
