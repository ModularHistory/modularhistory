from django.db import models
from django.utils.translation import ugettext_lazy as _


class TitledModel(models.Model):
    """Base model for models of which instances should have a title."""

    title = models.CharField(
        verbose_name=_('title'),
        max_length=120,
        blank=True,
        help_text=('This value can be used as a page header and/or title attribute.'),
    )

    class Meta:
        abstract = True
