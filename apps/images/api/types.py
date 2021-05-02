import graphene

from apps.graph.types import ModuleType
from apps.images.models.image import Image


class ImageType(ModuleType):
    """GraphQL type for the Image model."""

    class Meta:
        model = Image
        exclude = []

    def resolve_model(self, *args) -> str:
        return 'images.image'
