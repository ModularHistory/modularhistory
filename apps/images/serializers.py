"""Serializers for the entities app."""

import serpy

from apps.search.api.serializers import SearchableModelSerializer


class ImageSerializer(SearchableModelSerializer):
    """Serializer for images."""

    srcUrl = serpy.StrField(attr='src_url')
    width = serpy.IntField()
    height = serpy.IntField()
    captionHtml = serpy.Field(attr='caption_html')
    providerString = serpy.Field(attr='provider_string')
    bgImgPosition = serpy.Field(attr='bg_img_position')

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'images.image'
