from typing import Optional

import serpy

from core.models.model import ModelSerializer

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
