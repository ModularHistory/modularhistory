from django.db import models


class LtreeField(models.TextField):
    description = 'ltree'

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        kwargs['null'] = True
        kwargs['default'] = None
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'ltree'


class Ancestor(models.Lookup):
    lookup_name = 'ancestor'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} @> {rhs}', params


class Descendant(models.Lookup):
    lookup_name = 'descendant'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} <@ {rhs}', params


LtreeField.register_lookup(Ancestor)
LtreeField.register_lookup(Descendant)
