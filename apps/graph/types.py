import graphene
from graphene_django.types import DjangoObjectType


class AbstractModuleType(graphene.ObjectType):

    # required in order to use the ModuleDetail component
    model = graphene.String()

    # required in order to render the admin link
    admin_url = graphene.String(source='admin_url')

    class Meta:
        abstract = True

    def resolve_model(self, *args) -> str:
        raise NotImplementedError


class ModuleType(DjangoObjectType, AbstractModuleType):
    """Abstract GraphQL type for modules."""

    class Meta:
        abstract = True
