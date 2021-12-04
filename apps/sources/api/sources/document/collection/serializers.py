from apps.moderation.serializers import ModeratedModelSerializer
from apps.places.api.serializers import PlaceSerializer
from apps.sources.models import Collection, Repository


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

    instant_search_fields = {
        'repository': {
            'model': 'sources.repository',
        },
    }

    repository_serialized = RepositorySerializer(read_only=True, source='repository')

    class Meta:
        model = Collection
        fields = ModeratedModelSerializer.Meta.fields + [
            'name',
            'repository',
            'repository_serialized',
            'url',
        ]
