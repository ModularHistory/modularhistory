"""Serializers for the entities app."""


from apps.places.models import Place
from core.models.model import TypedModelSerializer


class PlaceSerializer(TypedModelSerializer):
    """Serializer for places."""

    class Meta(TypedModelSerializer.Meta):
        model = Place
        fields = TypedModelSerializer.Meta.fields + [
            'string',
            'name',
            'preposition',
            'location',
        ]
        extra_kwargs = {
            'name': {'write_only': True},
            'preposition': {'required': False, 'write_only': True},
            'location': {'required': False, 'write_only': True},
        }
