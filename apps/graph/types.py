import graphene
from graphene_django.types import DjangoObjectType


class AbstractModuleType(graphene.ObjectType):
    """Base GraphQL type for model instances."""

    model = graphene.String()
    id = graphene.Int()
    admin_url = graphene.String(source='admin_url')
    absolute_url = graphene.String(source='absolute_url')

    class Meta:
        abstract = True

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to an object's `model` attribute."""
        raise NotImplementedError


class ModuleType(DjangoObjectType, AbstractModuleType):
    """Abstract GraphQL type for modules."""

    class Meta:
        abstract = True
