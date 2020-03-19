
import os
import sys

import django

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()


from sources.models import Document, Letter

for s in Document.objects.all():
    if s.url:
        s.information_url = s.url
        s.save()
for s in Letter.objects.all():
    if s.url:
        s.information_url = s.url
        s.save()


# from history import settings
# from django.db import transaction
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType


