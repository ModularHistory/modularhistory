from typing import Optional

from rest_framework import serializers

from apps.moderation.serializers import ModeratedModelSerializer
from core.models.model import ModelSerializer

ELASTICSEARCH_META_FIELDS_TO_CLEAN = ['id', 'index', 'doc_type']


class SearchableModelSerializer(ModeratedModelSerializer):
    """Base serializer for searchable models."""

    meta = serializers.SerializerMethodField(required=False)

    def get_meta(self, model) -> Optional[dict]:
        if not hasattr(model, 'meta'):
            return None
        meta = model.meta.to_dict().copy()
        for key in ELASTICSEARCH_META_FIELDS_TO_CLEAN:
            if key in meta:
                del meta[key]
        return meta

    class Meta(ModelSerializer.Meta):
        fields = ModelSerializer.Meta.fields + [
            'meta',
        ]
