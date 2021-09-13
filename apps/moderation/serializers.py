from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


def get_moderated_model_serializer(
    model_serializer: type[ModelSerializer],
) -> type[ModelSerializer]:
    """Return the serializer to be used for moderation of a moderated model.
    Adds 'fields' field to given model_serializer.
    """

    class ModeratedModelSerializer(model_serializer):
        fields = serializers.ReadOnlyField(source='get_moderated_fields')

        class Meta(model_serializer.Meta):
            fields = model_serializer.Meta.fields + ['fields']

    return ModeratedModelSerializer
