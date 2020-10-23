"""A modification of Django's JSONField."""

import json
from typing import Any, Dict, List, Optional, Type, Union

from django.core.exceptions import ValidationError
from django.db.models import JSONField as BaseJSONField, Model  # type: ignore
from jsonschema import exceptions as jsonschema_exceptions, validate


class JSONField(BaseJSONField):
    """
    A modification of Django's JSONField.

    Adds pre-save validation functionality.
    """

    schema: Optional[Union[str, Dict]]
    model: Type[Model]

    def __init__(self, *args, **kwargs):
        """Override `__init__`."""
        # Remove the `schema` param before calling regular __init__
        schema = kwargs.pop('schema', None)
        self.schema = schema

        # Use a default `default` value of dict (callable)
        kwargs['default'] = kwargs.get('default') or dict

        # Call the base JSONField's __init__
        super().__init__(*args, **kwargs)

    @property
    def _schema_data(self) -> Optional[Dict]:
        """Return the field's JSON schema as a Python object."""
        if not self.schema:
            return None
        return json.loads(self.schema) if isinstance(self.schema, str) else self.schema
        # model_file = inspect.getfile(self.model)
        # dirname = os.path.dirname(model_file)
        # # schema file related to model.py path
        # p = os.path.join(dirname, self.schema)
        # with open(p, 'r') as file:
        #     return json.loads(file.read())

    def _validate_schema(self, json_value):
        """Validate with JSON Schema."""
        # Disable JSON Schema validation when migrations are faked
        if self.schema and self.model.__module__ != '__fake__':
            try:
                validate(json_value, self._schema_data)
            except jsonschema_exceptions.ValidationError as error:
                raise ValidationError(f'{error}')

    def validate(self, json_value, model_instance):
        """Override `validate` to also validate with JSON Schema."""
        # Do regular validation
        super().validate(json_value, model_instance)
        # Do JSON Schema validation
        self._validate_schema(json_value)

    def pre_save(self, model_instance, add):
        """Override `pre_save` to validate with JSON Schema."""
        json_value = super().pre_save(model_instance, add)
        if json_value and not self.null:
            self._validate_schema(json_value)
        return json_value


class ExtraField:
    """TODO: add docstring."""

    name: str

    def __init__(self, json_field_name: str, null: bool = True, blank: bool = True):
        """TODO: add docstring."""
        self.json_field_name = json_field_name
        self.null = null
        self.blank = blank

    def __get__(self, instance: Model, owner: Type[Model] = None) -> Optional[Any]:
        """See https://docs.python.org/3/reference/datamodel.html#object.__get__."""
        if instance is None:
            return self
        json_value = getattr(instance, self.json_field_name)
        if isinstance(json_value, dict):
            return self.from_json(json_value.get(self.name, None))
        return None

    def __set__(self, instance: Model, value_to_store: Any):
        """See https://docs.python.org/3/reference/datamodel.html#object.__set__."""
        json_value = self.get_json_field_value(instance)

        # Transform the value to valid JSON
        value_to_store = self.to_json(value_to_store)

        # Set the attribute
        if value_to_store:
            json_value[self.name] = value_to_store
        elif self.null:
            # Remove the key from the JSON
            self.__delete__(instance)
        elif self.blank:
            json_value[self.name] = ''
        else:
            raise ValueError(f'Required field `{self.json_field_name}` has no value.')

        # Update the JSON field
        setattr(instance, self.json_field_name, json_value)

    def __set_name__(self, owner: Type[Model], name: str):
        """See https://docs.python.org/3/reference/datamodel.html#object.__set_name__."""
        self.name = name

    def __delete__(self, instance: Model):
        """See https://docs.python.org/3/reference/datamodel.html#object.__delete__."""
        json_value = self.get_json_field_value(instance)
        # If the value is null, remove the key from the JSON
        try:
            del json_value[self.name]
        except KeyError:
            pass

    @staticmethod
    def from_json(stored_value) -> Any:
        """Transform a JSON value to its intended Python value."""
        return stored_value

    @staticmethod
    def to_json(value_to_store) -> Union[str, int, List, Dict]:
        """Transform a value to a format suitable for storage in JSON."""
        return value_to_store

    def get_json_field_value(self, model_instance: Model):
        """Retrieve the value of the JSON field."""
        # Retrieve the full JSON value
        json_value = getattr(model_instance, self.json_field_name)
        # Make sure the JSON value is valid
        if json_value:
            if isinstance(json_value, dict):
                pass  # Expected
            else:
                raise ValueError(
                    f'Received invalid `json_value` of {type(json_value)}: {json_value}'
                )
        else:
            json_value = {}
        return json_value
