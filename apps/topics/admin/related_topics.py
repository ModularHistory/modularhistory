from typing import TYPE_CHECKING, Optional, Type

from django.contrib.admin import SimpleListFilter
from django.db.models import Model

from apps.admin.inlines import TabularInline
from core.constants.strings import NO, YES

if TYPE_CHECKING:
    from apps.topics.models.taggable_model import TaggableModel


class AbstractRelatedTopicsInline(TabularInline):
    """Abstract base inline for related topics."""

    model: Type[Model]
    autocomplete_fields = ['topic']
    verbose_name = 'tag'
    verbose_name_plural = 'tags'

    def get_extra(
        self, request, model_instance: Optional['TaggableModel'] = None, **kwargs
    ) -> int:
        """Return the number of extra (blank) input rows to display."""
        if model_instance and model_instance.tags.count():
            return 0
        return 1


class HasTagsFilter(SimpleListFilter):
    """Reusable filter for whether or not model instances have topic tags."""

    title = 'has tags'
    parameter_name = 'has_tags'

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        if self.value() == YES:
            return queryset.exclude(tags=None)
        if self.value() == NO:
            return queryset.filter(tags=None)
