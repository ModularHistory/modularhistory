"""Serializers for the entities app."""

import serpy

from apps.search.models.searchable_model import SearchableModelSerializer


class ImageSerializer(SearchableModelSerializer):
    """Serializer for images."""

    src_url = serpy.StrField()
    width = serpy.IntField()
    height = serpy.IntField()
    captionHtml = serpy.Field(attr='caption_html')
    providerString = serpy.Field(attr='provider_string')
    bg_img_position = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'images.image'
