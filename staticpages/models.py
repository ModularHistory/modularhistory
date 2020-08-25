from django.db import models
from django.contrib.flatpages.models import FlatPage


class AbstractFlatPage(FlatPage):
    class Meta:
        abstract = True


class StaticPage(AbstractFlatPage):
    meta_description = models.TextField(max_length=200)

    class Meta:
        # db_table = 'django_flatpage'
        # verbose_name = _('flat page')
        # verbose_name_plural = _('flat pages')
        ordering = ('url',)
