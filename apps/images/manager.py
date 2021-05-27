from typing import Optional

from django.db.models import Q

from apps.search.models.manager import SearchableModelManager, SearchableModelQuerySet


class ImageManager(SearchableModelManager):
    """Manager for images."""

    def search(
        self,
        query: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        entity_ids: Optional[list[int]] = None,
        topic_ids: Optional[list[int]] = None,
        rank: bool = False,
        suppress_unverified: bool = True,
        suppress_hidden: bool = True,
    ) -> 'SearchableModelQuerySet':
        """Return search results from apps.images."""
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
            qs = qs.filter(Q(entities__id__in=entity_ids))
        # Limit to specified topics
        if topic_ids:
            qs = qs.filter(Q(occurrences__tags__id__in=topic_ids))
        return qs
