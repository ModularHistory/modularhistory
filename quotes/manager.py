"""Manager class for quotes."""

from typing import List, Optional

from django.db.models import Q

from modularhistory.constants import OCCURRENCE_CT_ID
from modularhistory.models.manager import SearchableModelManager, SearchableModelQuerySet


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
        db: str = 'default'
    ) -> SearchableModelQuerySet:
        """Return search results from quotes."""
        qs = super().search(
            db=db,
            suppress_unverified=suppress_unverified
        ).filter(hidden=False).filter_by_date(
            start_year=start_year,
            end_year=end_year
        ).prefetch_related('attributees', 'images')
        # Limit to specified entities
        if entity_ids:
            qs = qs.filter(
                Q(attributees__id__in=entity_ids) |
                # Q(related_occurrences__involved_entities__id__in=entity_ids)
                Q(
                    relations__content_type_id=OCCURRENCE_CT_ID,
                    relations__object_id__in=entity_ids
                )
            )
        # Limit to specified topics
        if topic_ids:
            qs = qs.filter(
                Q(tags__topic__id__in=topic_ids) |
                Q(tags__topic__related_topics__id__in=topic_ids)
            )
        return qs
