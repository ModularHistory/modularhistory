from django.core.serializers.python import Serializer
from rest_framework import serializers


class ModeratedModelSerializer(serializers.ModelSerializer):

    moderated_fields_excludes = ['id', 'meta', 'admin_url', 'absolute_url']

    def get_moderated_fields(self) -> list[dict]:
        """
        Return a serialized list of the model's moderated fields.

        This can be used to construct forms intelligently in front-end code.
        """
        fields = []
        field: serializers.Field

        for field_name, field in self.get_fields().items():
            if field_name not in self.moderated_fields_excludes:
                fields.append(
                    {
                        'name': field_name,
                        'editable': not getattr(field, 'read_only', False),
                        'required': not getattr(field, 'required', False),
                        'allow_blank': not getattr(field, 'allow_blank', False),
                        'verbose_name': getattr(field, 'verbose_name', None),
                        'choices': getattr(field, 'choices', None),
                        'help_text': getattr(field, 'help_text', None),
                        'type': field.__class__.__name__,
                    }
                )
        return fields


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
        **options
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
