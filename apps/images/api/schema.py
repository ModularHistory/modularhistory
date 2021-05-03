import logging

import graphene

from apps.images.api.types import ImageType
from apps.images.models import Image


class Query(graphene.ObjectType):
    """GraphQL query for all images."""

    images = graphene.List(ImageType)
    image = graphene.Field(ImageType, slug=graphene.String())

    @staticmethod
    def resolve_images(root, info, **kwargs):
        return Image.objects.all()

    @staticmethod
    def resolve_image(root, info, slug: str):
        try:
            return Image.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Image.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
