from typing import Optional, TYPE_CHECKING

from django.contrib.admin import SimpleListFilter

from admin.admin import GenericTabularInline
from topics.models import TopicRelation

if TYPE_CHECKING:
    from history.models import TaggableModel


class RelatedTopicsInline(GenericTabularInline):
    """TODO: add docstring."""

    model = TopicRelation
    autocomplete_fields = ['topic']

    def get_extra(self, request, obj: Optional['TaggableModel'] = None, **kwargs) -> int:
        """Return the number of extra (blank) input rows to display."""
        if obj and obj.tags.count():
            return 0
        return 1


class HasTagsFilter(SimpleListFilter):
    """TODO: add docstring."""

    title = 'has tags'
    parameter_name = 'has_tags'

    def lookups(self, request, model_admin):
        """TODO: add docstring."""
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        """TODO: add docstring."""
        if self.value() == 'Yes':
            return queryset.exclude(tags=None)
        if self.value() == 'No':
            return queryset.filter(tags=None)
