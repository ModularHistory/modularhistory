from typing import TYPE_CHECKING

import graphene
from graphene_django.types import DjangoObjectType

from apps.moderation.api.schema import ChangeType

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AbstractModuleType(graphene.ObjectType):
    """Base GraphQL type for model instances."""

    model = graphene.String()
    pk = graphene.Int()
    admin_url = graphene.String(source='admin_url')
    absolute_url = graphene.String(source='absolute_url')
    changes = graphene.List(ChangeType)

    class Meta:
        abstract = True

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to an object's `model` attribute."""
        raise NotImplementedError

    @staticmethod
    def resolve_changes(root, *args) -> 'QuerySet':
        """Return the value to be assigned to an object's `model` attribute."""
        return root.changes.all()


class ModuleType(DjangoObjectType, AbstractModuleType):
    """Abstract GraphQL type for modules."""

    class Meta:
        abstract = True
