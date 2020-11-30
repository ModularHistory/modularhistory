from typing import List, Optional

from django.db.models import Q

from modularhistory.models.manager import TypedModelManager
from apps.search.models.manager import SearchableModelManager, SearchableModelQuerySet


class SourceManager(TypedModelManager, SearchableModelManager):
    """Manager for sources."""

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
    ) -> SearchableModelQuerySet:
        """Return search results from apps.sources."""
        qs = (
            super()
            .search(
                query=query,
                suppress_unverified=suppress_unverified,
                suppress_hidden=suppress_hidden,
            )
            .filter_by_date(start_year=start_year, end_year=end_year)
        )
        # Limit to specified entities
        if entity_ids:
            qs = qs.filter(Q(attributees__id__in=entity_ids))
        return qs
