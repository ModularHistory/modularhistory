"""Model classes for entity engagements, roles, affiliations, etc."""

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE

from modularhistory.fields import HistoricDateTimeField, HTMLField
from modularhistory.models import (
    Model
)

MAX_NAME_LENGTH: int = 100


class _Engagement(Model):
    """TODO: add docstring."""

    start_date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Affiliation(_Engagement):
    """TODO: add docstring."""
    entity = ForeignKey('entities.Entity', related_name='affiliations', on_delete=CASCADE)
    affiliated_entity = ForeignKey('entities.Entity', on_delete=CASCADE)
    roles = ManyToManyField(
        'Role',
        related_name='affiliations',
        through='RoleFulfillment',
        blank=True
    )

    class Meta:
        unique_together = ['entity', 'affiliated_entity', 'start_date']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return f'{self.entity} — {self.affiliated_entity}'


class Role(Model):
    """TODO: add docstring."""

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    description = HTMLField(null=True, blank=True)
    organization = ForeignKey('Entity', related_name='roles', on_delete=CASCADE)

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.name


class RoleFulfillment(_Engagement):
    """TODO: add docstring."""

    affiliation = ForeignKey(Affiliation, related_name='role_fulfillments', on_delete=CASCADE)
    role = ForeignKey(Role, related_name='fulfillments', on_delete=CASCADE)

    class Meta:
        unique_together = ['affiliation', 'role', 'start_date']
