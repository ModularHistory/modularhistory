"""Serializers for the entities app."""


from apps.places.models import Place
from core.models.model import DrfTypedModelSerializer


class PlaceSerializer(DrfTypedModelSerializer):
    """Serializer for places."""

    class Meta(DrfTypedModelSerializer.Meta):
        model = Place
        fields = DrfTypedModelSerializer.Meta.fields + [
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
