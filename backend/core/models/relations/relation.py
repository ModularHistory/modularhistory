"""Base model classes for relations, i.e., models that mediate m2m relationships."""

from core.models.model import ExtendedModel

FieldList = list[str]


class Relation(ExtendedModel):
    """An m2m intermediate relation."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True
