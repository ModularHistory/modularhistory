from apps.moderation.serializers import ModeratedModelSerializer
from apps.places.api.serializers import PlaceSerializer
from apps.sources.models import Collection, Repository
from core.models.model import ModelSerializer


class RepositorySerializer(ModeratedModelSerializer):
    """Serializer for document collections repositories."""

    location_serialized = PlaceSerializer(read_only=True, source='location')

    class Meta:
        model = Repository
        fields = ModeratedModelSerializer.Meta.fields + [
            'name',
            'owner',
            'location',
            'location_serialized',
        ]


class CollectionSerializer(ModeratedModelSerializer):
    """Serializer for document collections."""

    repository_serialized = RepositorySerializer(read_only=True, source='repository')

    class Meta:
        model = Collection
        fields = ModeratedModelSerializer.Meta.fields + [
            'name',
            'repository',
            'repository_serialized',
            'url',
        ]
