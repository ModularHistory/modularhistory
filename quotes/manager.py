"""Manager class for quotes."""

from typing import List, Optional

from django.db.models import Q

from modularhistory.constants.misc import OCCURRENCE_CT_ID
from search.models.manager import SearchableModelManager, SearchableModelQuerySet


class QuoteManager(SearchableModelManager):
    """Manager for quotes."""

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
        """Return search results from quotes."""
        qs = (
            super()
            .search(
                query=query,
                suppress_unverified=suppress_unverified,
                suppress_hidden=suppress_hidden,
            )
            .filter(hidden=False)
            .filter_by_date(start_year=start_year, end_year=end_year)
        )
        # Limit to specified entities
        if entity_ids:
            qs = qs.filter(
                Q(attributees__id__in=entity_ids)
                | Q(
                    relations__content_type_id=OCCURRENCE_CT_ID,
                    relations__object_id__in=entity_ids,
                )
            )
        # Limit to specified topics
        if topic_ids:
            qs = qs.filter(
                Q(tags__topic__id__in=topic_ids)
                | Q(tags__topic__related_topics__id__in=topic_ids)
            )
        return qs
