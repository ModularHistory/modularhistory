
import os
import sys

import django

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()


from sources.models import Source, Citation
from quotes.models import QuoteSourceReference, Quote
from occurrences.models import OccurrenceSourceReference, Occurrence
from django.contrib.contenttypes.models import ContentType


Citation.objects.all().delete()

quote = ContentType.objects.get_for_model(Quote)
for qsr in QuoteSourceReference.objects.all():
    Citation.objects.create(source=qsr.source, content_type=quote,
                            content_object=qsr.quote, object_id=qsr.quote.id,
                            position=qsr.position, page_number=qsr.page_number,
                            end_page_number=qsr.end_page_number,
                            citation_phrase=qsr.citation_phrase)

occurrence = ContentType.objects.get_for_model(Occurrence)
for osr in OccurrenceSourceReference.objects.all():
    Citation.objects.create(source=osr.source, content_type=occurrence,
                            content_object=osr.occurrence, object_id=osr.occurrence.id,
                            position=osr.position, page_number=osr.page_number,
                            end_page_number=osr.end_page_number,
                            citation_phrase=osr.citation_phrase)

for osr in OccurrenceSourceReference.objects.all():
    if not Citation.objects.filter(source=osr.source, content_type=occurrence,
                                   object_id=osr.occurrence.id, position=osr.position,
                                   page_number=osr.page_number).exists():
        raise Exception('Failed to create Citation objects for all OSRs')

for qsr in QuoteSourceReference.objects.all():
    if not Citation.objects.filter(source=qsr.source, content_type=quote,
                                   object_id=qsr.quote.id, position=qsr.position,
                                   page_number=qsr.page_number).exists():
        raise Exception('Failed to create Citation objects for all QSRs')

# from history import settings
# from django.db import transaction
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType


