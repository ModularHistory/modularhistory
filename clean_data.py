
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

from quotes.models import Quote
from topics.models import Topic, TopicQuoteRelation
from entities.models import Entity

joseph = Entity.objects.filter(name='Joseph Smith, Jr.')[0]
brigham = Entity.objects.filter(name='Brigham Young')[0]

joseph_topic = Topic.objects.get(key='Joseph Smith')
brigham_topic = Topic.objects.get(key='Brigham Young')

for quote in Quote.objects.filter(attributee=joseph):
    if not TopicQuoteRelation.objects.filter(topic=joseph_topic, quote=quote).exists():
        TopicQuoteRelation.objects.create(topic=joseph_topic, quote=quote)

for quote in Quote.objects.filter(attributee=brigham):
    if not TopicQuoteRelation.objects.filter(topic=brigham_topic, quote=quote).exists():
        TopicQuoteRelation.objects.create(topic=brigham_topic, quote=quote)

