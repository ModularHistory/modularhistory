from django.contrib.admin import SimpleListFilter

from history.admin import GenericTabularInline
from topics.models import TopicRelation


class RelatedTopicsInline(GenericTabularInline):
    """TODO: add docstring."""

    model = TopicRelation
    autocomplete_fields = ['topic']
    extra = 1

    # def get_extra(self, request, obj=None, **kwargs):
    #     if obj and obj.topic_relations.count():
    #         return 0
    #     return 1


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
