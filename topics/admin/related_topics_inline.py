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
