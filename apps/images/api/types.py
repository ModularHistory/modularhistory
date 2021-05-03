import graphene

from apps.graph.types import ModuleType
from apps.images.models.image import Image


class ImageType(ModuleType):
    """GraphQL type for the Image model."""

    class Meta:
        model = Image
        exclude = []

    @staticmethod
    def resolve_model(root, *args) -> str:
        return 'images.image'
