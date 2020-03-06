# from sys import stderr
from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.forms import Field

from history.forms import SimpleArrayField


class ArrayField(PostgresArrayField):
    def formfield(self, **kwargs) -> Field:
        return super(PostgresArrayField, self).formfield(**{
            'form_class': SimpleArrayField,
            'base_field': self.base_field.formfield(),
            'max_length': self.size,
            **kwargs,
        })
