"""Base model classes for relations, i.e., models that mediate m2m relationships."""


from django.db import models

from .relation import Relation


class PositionedRelation(Relation):
    """An m2m intermediate relation sortable by position."""

    position = models.PositiveSmallIntegerField(blank=True, default=0)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    @property
    def number(self) -> int:
        """Return the citation's 1-based index."""
        return self.position + 1
