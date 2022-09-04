from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError

from apps.graph.types import ModuleType
from apps.images.models import Image
from apps.images.models.image import Image


class ImageType(ModuleType):
    """GraphQL type for the Image model."""

    src_url = graphene.String()
    caption_html = graphene.String()
    provider_string = graphene.String()

    class Meta:
        model = Image
        exclude = []

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to an image's `model` attribute."""
        return 'images.image'


class Query(graphene.ObjectType):
    """GraphQL query for all images."""

    images = graphene.List(ImageType)
    image = graphene.Field(ImageType, slug=graphene.String())

    @staticmethod
    def resolve_images(root, info, **kwargs):
        """Return the queryset against which an 'images' query should be executed."""
        return Image.objects.all()

    @staticmethod
    def resolve_image(root, info, slug: str) -> Optional[Image]:
        """Return the image specified by an 'image' query."""
        try:
            return Image.objects.get(slug=slug)
        except ObjectDoesNotExist:
            if slug.isnumeric():
                try:
                    return Image.objects.get(pk=int(slug))
                except GraphQLError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
