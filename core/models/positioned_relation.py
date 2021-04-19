"""Base model class for positioned relations."""

from typing import List, Type

from django.db import models
from typedmodels.models import TypedModel as BaseTypedModel

from .model import Model

FieldList = List[str]

# TODO: Extend BaseTypedModel when it's possible.
# Currently, only one level of inheritance from BaseTypedModel is permitted, unfortunately.
TypedModel: Type[BaseTypedModel] = BaseTypedModel

# TODO: https://docs.djangoproject.com/en/3.1/topics/db/optimization/


class PositionedRelation(Model):
    """An m2m intermediate relation sortable by position."""

    position = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        """Meta options for PositionedRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        abstract = True
