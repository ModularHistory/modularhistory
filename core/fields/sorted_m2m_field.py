from sortedm2m.fields import SortedManyToManyField as BaseSortedManyToManyField

from core.models.positioned_relation import PositionedRelation


# https://github.com/jazzband/django-sortedm2m/blob/master/sortedm2m/fields.py
class SortedManyToManyField(BaseSortedManyToManyField):
    """Wrapper for SortedManyToManyField."""

    def __init__(self, to, sorted=True, base_class=None, **kwargs):
        if not base_class:
            base_class = PositionedRelation
            kwargs['sort_value_field_name'] = 'position'
        super().__init__(to, sorted=sorted, base_class=base_class, **kwargs)
