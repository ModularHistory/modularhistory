"""Base model class for positioned relations."""

from typing import List

from django.db import models

from .model import Model

FieldList = List[str]


class PositionedRelation(Model):
    """An m2m intermediate relation sortable by position."""

    position = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        """Meta options for PositionedRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    def __str__(self) -> str:
        return f''
