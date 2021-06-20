from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError

from apps.images.api.types import ImageType
from apps.images.models import Image


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
