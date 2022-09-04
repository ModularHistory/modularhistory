"""Base model classes for moderated models mediating m2m relationships."""

from apps.moderation.models.moderated_model import ModeratedModel

from .positioned import PositionedRelation
from .relation import Relation


class ModeratedRelation(ModeratedModel, Relation):
    """A moderated m2m intermediate relation."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True


class ModeratedPositionedRelation(ModeratedModel, PositionedRelation):
    """A moderated m2m intermediate relation sortable by position."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True
