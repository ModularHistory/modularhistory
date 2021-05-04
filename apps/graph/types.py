import graphene
from graphene_django.types import DjangoObjectType


class AbstractModuleType(graphene.ObjectType):

    # required in order to use the ModuleDetail component
    model = graphene.String()

    # required in order to render the admin link
    admin_url = graphene.String(source='admin_url')

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
