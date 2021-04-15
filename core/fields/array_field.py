from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.forms import Field

from core.forms import SimpleArrayField


class ArrayField(PostgresArrayField):
    """An array field."""

    def formfield(self, **kwargs) -> Field:
        """Construct the field to be used in forms."""
        return super(PostgresArrayField, self).formfield(
            **{
                'form_class': SimpleArrayField,
                'base_field': self.base_field.formfield(),
                'max_length': self.size,
                **kwargs,
            }
        )
