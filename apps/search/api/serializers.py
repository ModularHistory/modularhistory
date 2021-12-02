from typing import Optional

import serpy
from rest_framework import serializers

from core.models.model import DrfModelSerializer, ModelSerializer

ELASTICSEARCH_META_FIELDS_TO_CLEAN = ['id', 'index', 'doc_type']


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    meta = serpy.MethodField()

    def get_meta(self, model) -> Optional[dict]:
        if not hasattr(model, 'meta'):
            return None
        meta = model.meta.to_dict().copy()
        for key in ELASTICSEARCH_META_FIELDS_TO_CLEAN:
            if key in meta:
                del meta[key]
        return meta


class DrfSearchableModelSerializer(DrfModelSerializer):
    """Base serializer for searchable models."""

    # TODO: 'model' field should be defined in DrfModelSerializer but ArticleSerializer cannot resolve 'model' field if it's defined there
    model = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField(required=False)

    def get_meta(self, model) -> Optional[dict]:
        if not hasattr(model, 'meta'):
            return None
        meta = model.meta.to_dict().copy()
        for key in ELASTICSEARCH_META_FIELDS_TO_CLEAN:
            if key in meta:
                del meta[key]
        return meta

    class Meta(DrfModelSerializer.Meta):
        fields = DrfModelSerializer.Meta.fields + [
            'model',
            'meta',
        ]
