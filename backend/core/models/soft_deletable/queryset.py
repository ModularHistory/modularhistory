from typing import TYPE_CHECKING

from django.db.models.query import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from core.models.soft_deletable.model import SoftDeletableModel


class SoftDeletableQuerySet(QuerySet):
    """Default queryset for the SoftDeletableManager.

    Takes care of "lazily evaluating" safedelete QuerySets. QuerySets passed
    within the ``SoftDeletableQuerySet`` will have all of the models available.
    The deleted policy is evaluated at the very end of the chain when the
    QuerySet itself is evaluated.
    """

    def delete(self):
        """Override bulk delete behavior."""
        assert self.query.can_filter(), 'Cannot use "limit" or "offset" with delete.'
        self.update(deleted=timezone.now())
        self._result_cache = None

    delete.alters_data = True

    def undelete(self):
        """Undelete soft-deleted instances."""
        assert self.query.can_filter(), 'Cannot use "limit" or "offset" with undelete.'
        # TODO: Replace this by bulk update if we can (need to call pre/post-save signal)
        obj: 'SoftDeletableModel'
        for obj in self.all():
            obj.undelete()
        self._result_cache = None

    undelete.alters_data = True
