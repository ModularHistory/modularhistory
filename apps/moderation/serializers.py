from django.core.exceptions import FieldDoesNotExist
from django.core.serializers.python import Serializer
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.serializers import ListSerializer

from core.fields import HTMLField
from core.models.model import ModelSerializer

common_instant_search_fields = {
    'attributees': {'model': 'entities.entity'},
    'related_entities': {'model': 'entities.entity'},
    'tags': {'model': 'topics.topic'},
    'location': {'model': 'places.place'},
    'images': {'model': 'images.image'},
}


class ModeratedModelSerializer(ModelSerializer):
    excluded_moderated_fields = ['id', 'meta', 'admin_url', 'absolute_url', 'cached_tags']

    instant_search_fields = {}

    # Child classes can override this to type field name and return choices via #get_type_field_choices
    # could be improved in the future to support multiple types
    type_field_name: str = None

    change_id = serializers.SerializerMethodField()

    def get_change_id(self, obj):
        from pprint import pprint

        pprint(obj.__dict__)
        return obj.change_in_progress.id if obj.change_in_progress else None

    def get_instant_search_fields(self) -> dict:
        return common_instant_search_fields | self.instant_search_fields

    def get_instant_search_field(self, field_name: str):
        field = self.get_instant_search_fields().get(field_name)
        if field:
            field_info = {'model': field['model']}
            if 'filters' in field:
                field_info['filters'] = field['filters']
            return field_info
        return None

    def get_type_field_choices(self, field):
        """
        Return a list of choices for the type field.
        """
        return None

    def get_choices_for_field(self, field, field_name: str):
        if field_name in self.get_instant_search_fields():
            return None
        if self.type_field_name and field_name == self.type_field_name:
            return self.get_type_field_choices(field)
        return getattr(field, 'choices', None)

    def get_moderated_fields(self) -> list[dict]:
        """
        Return a serialized list of the model's moderated fields.

        This can be used to construct forms intelligently in front-end code.
        """
        fields = []
        field: serializers.Field

        for field_name, field in self.get_fields().items():
            is_editable = not getattr(field, 'read_only', False)
            if is_editable and field_name not in self.excluded_moderated_fields:
                data = {
                    'name': field_name,
                    'type': field.__class__.__name__,
                    'editable': True,  # TODO: remove after front-end code is updated
                    'required': getattr(field, 'required', False),
                    'allow_blank': getattr(field, 'allow_blank', False)
                    if isinstance(field, CharField)
                    else None,
                    'verbose_name': getattr(field, 'verbose_name', None),
                    'help_text': getattr(field, 'help_text', None),
                    'choices': self.get_choices_for_field(field, field_name),
                }

                instant_search_field = self.get_instant_search_field(field_name)
                if instant_search_field:
                    data.update({'instant_search': instant_search_field})

                try:
                    if isinstance(self.Meta.model._meta.get_field(field_name), HTMLField):
                        data.update({'is_html': True})
                except FieldDoesNotExist:
                    pass

                if isinstance(field, ListSerializer) and isinstance(
                    field.child, ModeratedModelSerializer
                ):
                    data.update({'child_fields': field.child.get_moderated_fields()})

                fields.append(data)
        return fields

    class Meta(ModelSerializer.Meta):
        fields = ModelSerializer.Meta.fields + ['change_id']


class PythonSerializer(Serializer):
    """
    Patched version of django Serializer that uses model.fields instead of local_fields to include parent inherited fields in serialization.
    Patch is needed due to a bug where it won't save fields of parent model, when using multi-table inheritance (ex: Source child models)
    """

    def serialize(
        self,
        queryset,
        *,
        stream=None,
        fields=None,
        use_natural_foreign_keys=False,
        use_natural_primary_keys=False,
        progress_output=None,
        object_count=0,
        **options,
    ):
        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = stream if stream is not None else self.stream_class()
        self.selected_fields = fields
        self.use_natural_foreign_keys = use_natural_foreign_keys
        self.use_natural_primary_keys = use_natural_primary_keys
        progress_bar = self.progress_class(progress_output, object_count)

        self.start_serialization()
        self.first = True
        for count, obj in enumerate(queryset, start=1):
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            # When using natural primary keys, retrieve the pk field of the
            # parent for multi-table inheritance child models. That field must
            # be serialized, otherwise deserialization isn't possible.
            if self.use_natural_primary_keys:
                pk = concrete_model._meta.pk
                pk_parent = pk if pk.remote_field and pk.remote_field.parent_link else None
            else:
                pk_parent = None

            # patch: local_fields -> fields to get all fields including inherited
            for field in concrete_model._meta.fields:
                if field.serialize or field is pk_parent:
                    if field.remote_field is None:
                        if (
                            self.selected_fields is None
                            or field.attname in self.selected_fields
                        ):
                            self.handle_field(obj, field)
                    else:
                        if (
                            self.selected_fields is None
                            or field.attname[:-3] in self.selected_fields
                        ):
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.local_many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
            progress_bar.update(count)
            self.first = self.first and False
        self.end_serialization()
        return self.getvalue()
