"""Serializers for the entities app."""


from apps.places.models import Place
from core.models.model import ModelSerializerDrf


class PlaceModelSerializer(ModelSerializerDrf):
    """Serializer for places."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'places.place'

    class Meta(ModelSerializerDrf.Meta):
        model = Place
        fields = ModelSerializerDrf.Meta.fields + ['string']
