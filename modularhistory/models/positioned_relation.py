"""Base model class for positioned relations."""

from typing import List, Type

from django.db.models import Model as DjangoModel
from typedmodels.models import TypedModel as BaseTypedModel

from django.db import models

FieldList = List[str]

# TODO: Extend BaseTypedModel when it's possible.
# Currently, only one level of inheritance from BaseTypedModel is permitted, unfortunately.
TypedModel: Type[BaseTypedModel] = BaseTypedModel

# TODO: https://docs.djangoproject.com/en/3.1/topics/db/optimization/


class PositionedRelation(DjangoModel):
    """An m2m intermediate relation sortable by position."""

    position = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
