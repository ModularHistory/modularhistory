from django.db import models
from django.db.models import ForeignKey, CASCADE

from history.models import Model


class HolyBook(Model):
    collection = ForeignKey(
        'Collection', related_name='%(class)s',
        null=True, blank=True,
        on_delete=CASCADE
    )
    collection_number = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='aka acquisition number'
    )
    location_info = models.CharField(
        max_length=400, null=True, blank=True,
        help_text='Ex: John H. Alexander Papers, Series 1: Correspondence, 1831-1848, Folder 1'
    )

    class Meta:
        abstract = True
