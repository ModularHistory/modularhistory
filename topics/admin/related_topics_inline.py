from admin import GenericTabularInline
from ..models import TopicRelation


class RelatedTopicsInline(GenericTabularInline):
    model = TopicRelation
    autocomplete_fields = ['topic']
    # readonly_fields = ['quote_pk']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.topic_relations.count():
            return 0
        return 1
