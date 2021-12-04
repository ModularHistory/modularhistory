import pytest

from apps.moderation.serializers import ModeratedModelSerializer
from apps.search.documents import instant_search_documents_map
from core.fields import HTMLField

from .moderated_serializers import MODERATED_SERIALIZERS as serializers


@pytest.mark.django_db()
class TestModeratedSerializers:
    @classmethod
    def _test_moderated_fields(cls, fields, serializer):
        for field in fields:
            field_name = field['name']
            assert field_name, 'Field name is empty'

            if isinstance(serializer.Meta.model._meta.get_field(field_name), HTMLField):
                assert field['is_html'], 'Field is HTMLField but is_html is False'

            cls._test_moderated_relation_field(field, serializer)

    @classmethod
    def _test_moderated_relation_field(cls, field, serializer):
        field_type = field['type']
        if field_type in ['PrimaryKeyRelatedField', 'ManyRelatedField']:
            choices = field['choices']

            # we might have exceptions to this rule in the future
            assert choices is None, 'Relation field has choices, expecting instant field'

            if choices is None:
                cls._test_moderated_relation_instant_search_field(field)
        elif field_type == 'ListSerializer':
            child_fields = field['child_fields']
            assert child_fields, 'ListSerializer field has no child fields'
            serializer = serializer.get_fields()[field['name']].child
            cls._test_moderated_fields(child_fields, serializer)

    @classmethod
    def _test_moderated_relation_instant_search_field(cls, field):
        instant_search = field['instant_search']
        model = instant_search['model']
        assert field['instant_search'], 'Relation field has no choices and no instant_search'

        if model != 'parent':
            assert (
                instant_search['model'] in instant_search_documents_map
            ), 'Instant search model is not defined in instant search documents map'

        if 'filters' in instant_search:
            filters = instant_search['filters']
            for filter_name in filters:
                assert (
                    filter_name
                    in instant_search_documents_map[instant_search['model']].filter_fields
                ), 'This filter is not defined in instant search documents map'

    def test_moderated_fields(self):
        assert len(serializers) > 0, 'No serializers found'

        for serializer in serializers:
            assert not isinstance(
                serializer, ModeratedModelSerializer
            ), 'Serializer is not a ModeratedModelSerializer'

            serializer_instance = serializer()
            fields = serializer_instance.get_moderated_fields()
            self._test_moderated_fields(fields, serializer_instance)
