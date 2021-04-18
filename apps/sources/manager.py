from typing import List, Optional

from django.db.models import Q
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet

from apps.search.models.manager import SearchableModelManager, SearchableModelQuerySet


class PolymorphicSourceQuerySet(PolymorphicQuerySet, SearchableModelQuerySet):
    """Add search capability to PolymorphicQuerySet."""


class PolymorphicSourceManager(PolymorphicManager, SearchableModelManager):
    def get_queryset(self):
        return super().get_queryset()

    def search(
        self,
        query: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        entity_ids: Optional[List[int]] = None,
        topic_ids: Optional[List[int]] = None,
        rank: bool = False,
        suppress_unverified: bool = True,
        suppress_hidden: bool = True,
    ) -> 'PolymorphicSourceQuerySet':
        """Return search results."""
        qs = (
            super()
            # https://django-polymorphic.readthedocs.io/en/stable/advanced.html?highlight=non_polymorphic#non-polymorphic-queries
            .search(
                query=query,
                suppress_unverified=suppress_unverified,
                suppress_hidden=suppress_hidden,
            ).filter_by_date(start_year=start_year, end_year=end_year)
            # Return a queryset of Source instances, not instances of child models.
            .non_polymorphic()
        )
        # Filter by specified entities.
        if entity_ids:
            qs = qs.filter(Q(attributees__id__in=entity_ids))
        return qs
