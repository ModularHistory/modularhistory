from django.contrib.admin import SimpleListFilter

from admin import GenericTabularInline
from ..models import TopicRelation


class RelatedTopicsInline(GenericTabularInline):
    model = TopicRelation
    autocomplete_fields = ['topic']
    extra = 1

    # def get_extra(self, request, obj=None, **kwargs):
    #     if obj and obj.topic_relations.count():
    #         return 0
    #     return 1


class HasTagsFilter(SimpleListFilter):
    title = 'has tags'
    parameter_name = 'has_tags'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.exclude(tags=None)
        if self.value() == 'No':
            return queryset.filter(tags=None)