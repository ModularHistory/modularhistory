"""Serializers for the entities app."""

import serpy

from apps.search.models.searchable_model import SearchableModelSerializer


class ImageSerializer(SearchableModelSerializer):
    """Serializer for images."""

    src_url = serpy.StrField()
    width = serpy.IntField()
    height = serpy.IntField()
    caption_html = serpy.Field()
    provider_string = serpy.Field()
    bg_img_position = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'images.image'
