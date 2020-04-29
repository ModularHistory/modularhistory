from admin import GenericTabularInline
from .. import models


class RelatedQuotesInline(GenericTabularInline):
    model = models.QuoteRelation
    autocomplete_fields = ['quote']
    readonly_fields = ['quote_pk']
    # verbose_name = 'citation'
    # verbose_name_plural = 'citations'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.quote_relations.count():
            return 0
        return 1
