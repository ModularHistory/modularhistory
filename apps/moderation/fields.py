import re
from pprint import pprint
from typing import Any, Optional, Union

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework.utils.encoders import JSONEncoder


def serialize(value_set):
    return serializers.serialize(
        'json',
        value_set,
        cls=JSONEncoder,
    )


def deserialize(value):
    return serializers.deserialize(
        'json',
        value.encode(settings.DEFAULT_CHARSET),
        ignorenonexistent=True,
        cls=JSONEncoder,
    )


class SerializedObjectField(models.JSONField):
    """Model field for storing a serialized model instance."""

    def __init__(self, *args, **kwargs):
        """Construct the field."""
        kwargs['encoder'] = JSONEncoder
        # kwargs['decoder'] = ''  # TODO?
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple:
        """Reduce the field to its serialized form for migrations."""
        name, path, args, kwargs = super().deconstruct()
        del kwargs['encoder']
        return name, path, args, kwargs

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.from_db_value
    def from_db_value(self, value: Optional[str], *args) -> Optional[models.Model]:
        """
        Convert a value as returned by the database to a Python object.
        This method is the reverse of `get_prep_value()`.
        """
        # value: Union[list, dict] = super().from_db_value(value, *args)
        return self._deserialize(value)

    def get_prep_value(self, value: Any) -> Any:
        """
        Convert a Python object to the value to be stored in the database.
        This method is the reverse of `from_db_value()`.
        """
        return self._serialize(value)

    # https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(
        self, value: Optional[Union[models.Model, dict, list, str]]
    ) -> Optional[models.Model]:
        """
        Convert the value into the correct Python object.
        This method acts as the reverse of value_to_string(), and is also called in clean().
        """
        if not value:
            return None
        elif isinstance(value, models.Model):
            return value
        elif isinstance(value, str):
            return self._deserialize(value)
        elif isinstance(value, dict):
            raise Exception(value)
        elif isinstance(value, list):
            raise Exception(value)
        raise TypeError(value)

    def _serialize(self, value):
        print('\n>>> _serialize:')
        if not value:
            return ''
        value_set = [value]
        if value._meta.parents:
            value_set += [
                getattr(value, f.name)
                for f in list(value._meta.parents.values())
                if f is not None
            ]
        serialized_value = serialize(value_set)
        pprint(re.match(r'.+("date".{30})', serialized_value).group(1))
        return serialized_value

    def _deserialize(self, value):
        print('\n>>> _deserialize:')
        obj_generator = deserialize(value)
        obj = next(obj_generator).object
        for parent in obj_generator:
            for f in parent.object._meta.fields:
                try:
                    setattr(obj, f.name, getattr(parent.object, f.name))
                except ObjectDoesNotExist:
                    try:
                        # Try to set non-existant foreign key reference to None
                        setattr(obj, f.name, None)
                    except ValueError:
                        # Return None for changed_object if None not allowed
                        return None
        return obj
