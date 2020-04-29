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
from occurrences.models import Occurrence
from quotes.models import QuoteRelation
from topics.models import TopicQuoteRelation, Topic, OccurrenceTopicRelation, Relation


occurrence_ct = ContentType.objects.get_for_model(Occurrence)

for _otr in OccurrenceTopicRelation.objects.all():
    otr: OccurrenceTopicRelation = _otr
    Relation.objects.get_or_create(
            topic=otr.topic, object_id=otr.occurrence_id,
            content_type=occurrence_ct
    )
