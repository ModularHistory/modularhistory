from typing import Optional

from django.db import models


class ManyToManyForeignKey(models.ForeignKey):
    """Foreign key on a m2m intermediate model."""

    def __init__(self, *args, related_name: Optional[str] = None, **kwargs):
        """Construct the field."""
        to = kwargs.get('to')
        if len(args) and not to:
            to = args[0]
        kwargs['on_delete'] = kwargs.get('on_delete') or models.CASCADE
        kwargs['related_name'] = related_name or '%(app_label)s_%(class)s_relations'
        super().__init__(**kwargs)
