from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import DateTimeField
from django.utils.translation import ugettext_lazy as _

from core.models.model import ExtendedModel


class Feature(ExtendedModel):
    """A model for featured contents"""

    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )
    content_type.content_type_filter = True
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id',
    )
    start_date = DateTimeField(
        verbose_name=_('start date'),
        null=True,
        blank=True,
    )
    end_date = DateTimeField(
        verbose_name=_('end date'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.content_object}'
