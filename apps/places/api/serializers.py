"""Serializers for the entities app."""


from apps.places.models import Place
from core.models.model import TypedModelSerializerDrf


class PlaceModelSerializer(TypedModelSerializerDrf):
    """Serializer for places."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'places.place'

    class Meta(TypedModelSerializerDrf.Meta):
        model = Place
        fields = TypedModelSerializerDrf.Meta.fields + ['string']
