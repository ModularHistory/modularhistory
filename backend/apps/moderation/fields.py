import json
from typing import Optional, Union

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.db.models import JSONField, Model
from rest_framework.utils.encoders import JSONEncoder

from apps.moderation.serializers import PythonSerializer

SerializedModel = list[dict]


class SerializedObjectField(JSONField):
    """Model field for storing a serialized model instance."""

    def __init__(self, *args, **kwargs):
        """Construct the field."""
        kwargs['encoder'] = JSONEncoder
        kwargs['editable'] = False
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple:
        """Reduce the field to its serialized form for migrations."""
        name, path, args, kwargs = super().deconstruct()
        del kwargs['encoder']
        del kwargs['editable']
        return name, path, args, kwargs

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.from_db_value
    def from_db_value(self, value: str, *args) -> Optional[Model]:
        """
        Convert a value as returned by the database to a Python object.

        This method is the reverse of `get_prep_value()`.
        """
        if value is None:
            return value
        return deserialize_instance(json.loads(value, cls=self.decoder))

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.get_prep_value
    def get_prep_value(self, value: Optional[Union[Model, SerializedModel, str]]) -> str:
        """
        Convert a Python object to the value to be stored in the database.

        This method is the reverse of `from_db_value()`.
        """
        if isinstance(value, Model):
            value = serialize_instance(value)
        return super().get_prep_value(value)

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.get_db_prep_value
    def get_db_prep_value(self, value, connection, prepared: bool) -> str:
        return self.get_prep_value(value)

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.pre_save
    def pre_save(self, model_instance: Model, add: bool) -> SerializedModel:
        """Preprocess the field value immediately before saving."""
        # Convert the field value from a model instance to a serialized Python object.
        value: Optional[Model] = getattr(model_instance, self.attname, None)
        return serialize_instance(value)

    # https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(
        self, value: Optional[Union[Model, SerializedModel, str]]
    ) -> Optional[Model]:
        """
        Convert the value into the correct Python object.

        This method acts as the reverse of value_to_string(), and is also called in clean().
        """
        value = super().to_python(value)
        if not value:
            return None
        elif isinstance(value, str):
            return self.from_db_value(value)
        elif isinstance(value, list):
            return deserialize_instance(value)
        elif isinstance(value, Model):
            return value
        raise TypeError(value)


def _deserialize(value_set: list, **options):
    yield from PythonDeserializer(value_set, **options)


def serialize_instance(instance: Model) -> SerializedModel:
    if not isinstance(instance, Model):
        raise TypeError(instance)
    fields = instance._meta.get_fields()
    for field in fields:
        is_string_field = field.get_internal_type() in ('CharField', 'TextField')
        if is_string_field and getattr(instance, field.name, None) is None:
            setattr(instance, field.name, '')
    value_set = [instance]
    # patch: disable adding parent models because patched PythonSerializer includes parent fields
    # if instance._meta.parents:
    #     value_set += [
    #         getattr(instance, f.name)
    #         for f in list(instance._meta.parents.values())
    #         if f is not None
    #     ]
    serialized_value = PythonSerializer().serialize(value_set)
    return serialized_value


def deserialize_instance(serialized_instance: SerializedModel) -> Model:
    """Given a serialized model instance, return a model instance."""
    obj_generator = _deserialize(serialized_instance, ignorenonexistent=True)
    unsaved_instance = next(obj_generator).object
    for parent in obj_generator:
        for f in parent.object._meta.fields:
            try:
                setattr(unsaved_instance, f.name, getattr(parent.object, f.name))
            except ObjectDoesNotExist:
                try:
                    # Try to set non-existant foreign key reference to None
                    setattr(unsaved_instance, f.name, None)
                except ValueError:
                    # Return None for changed_object if None not allowed
                    return None
    return unsaved_instance
