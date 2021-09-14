"""A modification of Django's JSONField."""

import json
import logging
from pprint import pformat
from typing import TYPE_CHECKING, Any, Optional, Union

from django.core.exceptions import ValidationError
from django.db.models import (  # type: ignore  # https://github.com/typeddjango/django-stubs/issues/439  # noqa: E501
    JSONField as BaseJSONField,
)
from jsonschema import exceptions as jsonschema_exceptions
from jsonschema import validate

if TYPE_CHECKING:
    from django.db.models import Model


class JSONField(BaseJSONField):
    """
    A modification of Django's JSONField.

    Adds pre-save validation functionality.
    """

    schema: Optional[Union[str, dict]]
    model: type['Model']

    def __init__(self, *args, schema=None, **kwargs):
        """Override `__init__`."""
        self.schema = schema

        # Use a default `default` value of dict (callable)
        kwargs['default'] = kwargs.get('default') or dict

        # Call the base JSONField's __init__
        super().__init__(*args, **kwargs)

    def validate(self, json_value, model_instance):
        """Override `validate` to also validate with JSON Schema."""
        # Do regular validation
        super().validate(json_value, model_instance)
        # Do JSON Schema validation
        self._validate_schema(json_value, model_instance)

    def pre_save(self, model_instance, add):
        """Before saving, validate with JSON Schema and remove null values."""
        json_value = super().pre_save(model_instance, add)
        if json_value:
            if not self.null:  # TODO: check this logic
                self._validate_schema(json_value, model_instance)
        return json_value

    def get_schema_data(self, model_instance) -> Optional[dict]:
        """Return the field's JSON schema as a Python object."""
        schema = self.schema
        if schema:
            if isinstance(schema, str):
                if hasattr(model_instance, schema):
                    schema = getattr(model_instance, schema, {})
            return json.loads(schema) if isinstance(schema, str) else schema
        return None

    def _validate_schema(self, json_value, model_instance):
        """Validate with JSON Schema."""
        # Disable JSON Schema validation when migrations are faked
        if self.model.__module__ != '__fake__':
            schema_data = self.get_schema_data(model_instance)
            if schema_data:
                try:
                    logging.debug(
                        f'Validating JSON value \n{pformat(json_value)}\n'
                        f'against schema: {schema_data}'
                    )
                    validate(json_value, schema_data)
                except (
                    jsonschema_exceptions.ValidationError,
                    jsonschema_exceptions.SchemaError,
                ) as error:
                    raise ValidationError(
                        f'JSON schema validation failed with {type(error)}; {error}\n'
                        f'\nEnsure the value complies with its schema:\n{schema_data}'
                    )


class ExtraField:
    """TODO: add docstring."""

    name: str

    def __init__(
        self,
        json_field_name: str,
        null: bool = True,
        blank: bool = True,
        help_text: Optional[str] = None,
    ):
        """TODO: add docstring."""
        self.json_field_name = json_field_name
        self.null = null
        self.blank = blank
        self.help_text = help_text

    def __get__(
        self, instance: Optional['Model'], owner: Optional[type['Model']] = None
    ) -> Optional[Any]:
        """See https://docs.python.org/3/reference/datamodel.html#object.__get__."""
        if instance is None:
            return self
        json_value = getattr(instance, self.json_field_name)
        if isinstance(json_value, dict):
            return self.from_json(json_value.get(self.name, None))
        return None

    def __set__(self, instance: 'Model', value_to_store: Any):
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

    def __set_name__(self, owner: type['Model'], name: str):
        """See https://docs.python.org/3/reference/datamodel.html#object.__set_name__."""
        self.name = name

    def __delete__(self, instance: 'Model'):
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
    def to_json(value_to_store) -> Union[str, int, dict]:
        """Transform a value to a format suitable for storage in JSON."""
        return value_to_store

    def get_json_field_value(self, model_instance: 'Model'):
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
