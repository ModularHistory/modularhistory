
import os
import sys

import django

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()


from quotes.models import Quote, QuoteAttribution

for q in Quote.objects.all():
    if q.attributee:
        if not q.attributees.exists():
            attributee = q.attributee
            QuoteAttribution.objects.create(quote=q, attributee=attributee)


# from history import settings
# from django.db import transaction
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType


