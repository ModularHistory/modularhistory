from typing import Type

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.moderation.models.moderated_model import ModeratedModel


def get_moderated_model_serializer(model_cls: Type[ModeratedModel]) -> Type[ModelSerializer]:
    """Return the serializer to be used for moderation of a moderated model."""

    class ModeratedModelSerializer(ModelSerializer):
        fields = serializers.ReadOnlyField(source='get_moderated_fields')

        class Meta:
            model = model_cls
            exclude = model.Moderation.excluded_fields

    return ModeratedModelSerializer
