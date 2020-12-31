"""Constants usable throughout the ModularHistory application."""

from django.contrib.contenttypes.models import ContentType


OCCURRENCE_CT_ID = ContentType.objects.get_by_natural_key(
    app_label='occurrences', model='occurrence'
)
QUOTE_CT_ID = ContentType.objects.get_by_natural_key(app_label='quotes', model='quote')
