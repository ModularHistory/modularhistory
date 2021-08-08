import json
from typing import Optional, Union

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.core.serializers.python import Serializer as PythonSerializer
from django.db.models import JSONField, Model
from rest_framework.utils.encoders import JSONEncoder


def deserialize(value_set: list, **options):
    yield from PythonDeserializer(value_set, **options)


class SerializedObjectField(JSONField):
    """Model field for storing a serialized model instance."""

    def __init__(self, *args, **kwargs):
        """Construct the field."""
        kwargs['encoder'] = JSONEncoder
        # kwargs['decoder'] = JSONEncoder
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple:
        """Reduce the field to its serialized form for migrations."""
        name, path, args, kwargs = super().deconstruct()
        del kwargs['encoder']
        return name, path, args, kwargs

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.from_db_value
    def from_db_value(self, value, *args) -> Optional[Model]:
        """
        Convert a value as returned by the database to a Python object.
        This method is the reverse of `get_prep_value()`.
        """
        if value is None:
            return value
        data = json.loads(value, cls=self.decoder)
        return self._deserialize(data)

    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.Field.get_prep_value
    def get_prep_value(self, value: Optional[Union[Model, str]]) -> str:
        """
        Convert a Python object to the value to be stored in the database.
        This method is the reverse of `from_db_value()`.
        """
        if isinstance(value, Model):
            return super().get_prep_value(self._serialize(value))
        return super().get_prep_value(value)

    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.Field.get_db_prep_value
    def get_db_prep_value(self, value, connection, prepared: bool) -> str:
        return super().get_db_prep_value(self.get_prep_value(value), connection, prepared)

    # https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(self, value: Optional[Union[Model, dict, list, str]]) -> Optional[Model]:
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
            return self._deserialize(value)
        elif isinstance(value, Model):
            return value
        raise TypeError(value)

    def _serialize(self, value: Model) -> list:
        if not isinstance(value, Model):
            raise TypeError(value)
        value_set = [value]
        if value._meta.parents:
            value_set += [
                getattr(value, f.name)
                for f in list(value._meta.parents.values())
                if f is not None
            ]
        serialized_value = PythonSerializer().serialize(value_set)
        # pprint(re.match(r'.+("date".{30})', serialized_value).group(1))
        return serialized_value

    def _deserialize(self, objects: list) -> Model:
        obj_generator = deserialize(objects, ignorenonexistent=True)
        try:
            obj = next(obj_generator)
        except Exception as err:
            print()
            raise
        unsaved_instance = obj.object
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
