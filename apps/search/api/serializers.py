from typing import Optional

import serpy

from rest_framework import serializers
from core.models.model import ModelSerializer, ModelSerializerDrf

ELASTICSEARCH_META_FIELDS_TO_CLEAN = ['id', 'index', 'doc_type']


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    absolute_url = serpy.StrField()
    admin_url = serpy.StrField()
    slug = serpy.StrField()
    cached_tags = serpy.Field()
    title = serpy.StrField()
    verified = serpy.BoolField()
    meta = serpy.MethodField()

    def get_meta(self, model) -> Optional[dict]:
        if not hasattr(model, 'meta'):
            return None
        meta = model.meta.to_dict()
        for key in ELASTICSEARCH_META_FIELDS_TO_CLEAN:
            # TODO: find out why in some cases it's already cleaned
            if key in meta:
                del meta[key]
        return model.meta.to_dict()


class SearchableModelSerializerDrf(ModelSerializerDrf):
    """Base serializer for searchable models."""

    absolute_url = serializers.CharField(required=False)
    admin_url = serializers.CharField(required=False)
    slug = serializers.CharField(required=False)
    cached_tags = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    verified = serializers.BooleanField(required=False)
    meta = serializers.SerializerMethodField(required=False)

    def get_meta(self, model) -> Optional[dict]:
        if not hasattr(model, 'meta'):
            return None
        meta = model.meta.to_dict()
        for key in ELASTICSEARCH_META_FIELDS_TO_CLEAN:
            # TODO: find out why in some cases it's already cleaned
            if key in meta:
                del meta[key]
        return model.meta.to_dict()

    class Meta(ModelSerializerDrf.Meta):
        fields = ModelSerializerDrf.Meta.fields + ['absolute_url', 'admin_url', 'slug', 'cached_tags', 'title', 'verified', 'meta']
