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
from quotes.models import QuoteRelation, Quote
from topics.models import TopicQuoteRelation, Topic, Relation, TopicRelation

occurrence_ct = ContentType.objects.get_for_model(Occurrence)
quote_ct = ContentType.objects.get_for_model(Quote)


for _relation in Relation.objects.all():
    relation: Relation = _relation
    TopicRelation.objects.get_or_create(
        topic=relation.topic, object_id=relation.object_id,
        content_type=relation.content_type
    )
