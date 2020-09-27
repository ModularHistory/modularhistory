# from sys import stderr
from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.forms import Field

from history.forms import SimpleArrayField


class ArrayField(PostgresArrayField):
    """TODO: add docstring."""
    def formfield(self, **kwargs) -> Field:
        """TODO: add docstring."""
        return super(PostgresArrayField, self).formfield(**{
            'form_class': SimpleArrayField,
            'base_field': self.base_field.formfield(),
            'max_length': self.size,
            **kwargs,
        })
