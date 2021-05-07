import serpy

from core.models.model import ModelSerializer


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    absoluteUrl = serpy.StrField(attr='absolute_url')
    adminUrl = serpy.StrField(attr='admin_url')
    slug = serpy.StrField()
    tagsHtml = serpy.StrField(attr='tags_html')
    title = serpy.StrField()
    verified = serpy.BoolField()
