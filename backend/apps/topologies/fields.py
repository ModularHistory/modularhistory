from django.db import models

# https://www.postgresql.org/docs/8.3/ltree.html


class LtreeField(models.TextField):
    """Field for storing a label tree (ltree)."""

    description = 'ltree'

    def __init__(self, *args, **kwargs):
        """Construct the ltree field."""
        kwargs['editable'] = False
        kwargs['null'] = True
        kwargs['default'] = None
        super().__init__(*args, **kwargs)

    def db_type(self, connection) -> str:
        """Return the data type that the ltree field uses in the database."""
        # Use the Postgres `ltree` type:
        # https://www.postgresql.org/docs/current/ltree.html
        return 'ltree'


class Ancestor(models.Lookup):
    """Lookup for instances with the specified ancestor, inclusive."""

    lookup_name = 'ancestor'

    def as_sql(self, qn, connection):
        """Return the SQL for the lookup."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} <@ {rhs}', params


class Descendant(models.Lookup):
    """Lookup for instances with the specified descendant, inclusive."""

    lookup_name = 'descendant'

    def as_sql(self, qn, connection):
        """Return the SQL for the lookup."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} @> {rhs}', params


LtreeField.register_lookup(Ancestor)
LtreeField.register_lookup(Descendant)
