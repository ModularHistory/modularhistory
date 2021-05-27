"""Base model class for positioned relations."""


from django.db import models

from .model import Model

FieldList = list[str]


class PositionedRelation(Model):
    """An m2m intermediate relation sortable by position."""

    position = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        """Meta options for PositionedRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True
