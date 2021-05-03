import graphene

from apps.graph.types import ModuleType
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
        return 'images.image'
