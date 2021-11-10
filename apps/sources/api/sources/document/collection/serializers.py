from apps.places.api.serializers import PlaceDrfSerializer
from apps.sources.models import Collection, Repository
from core.models.model import DrfModelSerializer


class RepositoryDrfSerializer(DrfModelSerializer):
    """Serializer for document collections repositories."""

    location_serialized = PlaceDrfSerializer(read_only=True, source='location')

    class Meta:
        model = Repository
        fields = DrfModelSerializer.Meta.fields + [
            'name',
            'owner',
            'location',
            'location_serialized',
        ]


class CollectionDrfSerializer(DrfModelSerializer):
    """Serializer for document collections."""

    repository_serialized = RepositoryDrfSerializer(read_only=True, source='repository')

    class Meta:
        model = Collection
        fields = DrfModelSerializer.Meta.fields + [
            'name',
            'repository',
            'repository_serialized',
            'url',
        ]
