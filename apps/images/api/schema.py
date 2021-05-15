import logging

import graphene

from apps.images.api.types import ImageType
from apps.images.models.image import Image


class Query(graphene.ObjectType):
    """GraphQL query for all images."""

    images = graphene.List(ImageType)
    image = graphene.Field(ImageType, slug=graphene.String())

    @staticmethod
    def resolve_images(root, info, **kwargs):
        """Return the queryset against which an 'images' query should be executed."""
        return Image.objects.all()

    @staticmethod
    def resolve_image(root, info, slug: str):
        """Return the image specified by an 'image' query."""
        try:
            return Image.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Image.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
