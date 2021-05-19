from typing import List, Optional

from django.db.models import Q
from polymorphic.managers import PolymorphicManager

from apps.occurrences.constants import OccurrenceTypes
from apps.search.models.manager import SearchableModelManager, SearchableModelQuerySet


class OccurrenceManager(PolymorphicManager, SearchableModelManager):
    """Manager for occurrences."""

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
    ) -> 'SearchableModelQuerySet':
        """Return search results from apps.occurrences."""
        qs = (
            super()
            .search(
                query=query,
                suppress_unverified=suppress_unverified,
                suppress_hidden=suppress_hidden,
            )
            .filter(hidden=False)
            .filter_by_date(start_year=start_year, end_year=end_year)
            .prefetch_related('citations', 'images')
        )
        # Limit to specified entities
        if entity_ids:
            qs = qs.filter(Q(involved_entities__id__in=entity_ids))
        # Limit to specified topics
        if topic_ids:
            qs = qs.filter(
                Q(tags__id__in=topic_ids) | Q(tags__related_topics__id__in=topic_ids)
            )
        return qs

    @staticmethod
    def prefetch_search_relatives(queryset):
        return queryset.prefetch_related(
            'tags',
            'citations',
            'images',
        )


class BirthManager(OccurrenceManager):
    def get_queryset(self) -> 'SearchableModelQuerySet':
        return super().get_queryset().filter(type=OccurrenceTypes.BIRTH.value)


class DeathManager(OccurrenceManager):
    def get_queryset(self) -> 'SearchableModelQuerySet':
        return super().get_queryset().filter(type=OccurrenceTypes.DEATH.value)


class PublicationManager(OccurrenceManager):
    def get_queryset(self) -> 'SearchableModelQuerySet':
        return super().get_queryset().filter(type=OccurrenceTypes.PUBLICATION.value)


class VerbalizationManager(OccurrenceManager):
    def get_queryset(self) -> 'SearchableModelQuerySet':
        return super().get_queryset().filter(type=OccurrenceTypes.VERBALIZATION.value)
