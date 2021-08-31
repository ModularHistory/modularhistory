import serpy


class FlatPageSerializer(serpy.Serializer):
    """Serializer for flatpages."""

    content = serpy.StrField()
