
import os
import sys

import django

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()


from topics.models import Topic, TopicRelation, TopicParentChildRelation


for t in Topic.objects.all():
    if t.parent and not t.parent_topics.exists():
        TopicParentChildRelation.objects.create(parent_topic=t.parent, child_topic=t)
    if t.related_topics.exists():
        for rt in t.related_topics.all():
            if rt not in t.related_topics2.all():
                TopicRelation.objects.create(from_topic=t, to_topic=rt)


# from history import settings
# from django.db import transaction
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType


