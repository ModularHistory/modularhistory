from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet

from apps.search.models.manager import SearchableModelManager, SearchableModelQuerySet


class PolymorphicSourceQuerySet(PolymorphicQuerySet, SearchableModelQuerySet):
    """Add search capability to PolymorphicQuerySet."""


class PolymorphicSourceManager(PolymorphicManager, SearchableModelManager):
    """Manager for sources."""
