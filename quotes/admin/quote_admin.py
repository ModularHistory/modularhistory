from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.urls import path

from admin import admin_site, Admin, TabularInline, GenericTabularInline
from entities.views import EntitySearchView
from history.models.taggable_model import TopicFilter
from occurrences.models import Occurrence
from sources.admin.citations import CitationsInline
from topics.admin import RelatedTopicsInline, HasTagsFilter
from topics.views import TagSearchView
from .filters import (
    AttributeeFilter,
    # AttributeeClassificationFilter,
    HasSourceFilter,
    AttributeeCountFilter,
    HasMultipleCitationsFilter
)
from .. import models


class OccurrencesInline(GenericTabularInline):
    model = models.QuoteRelation
    # readonly_fields = ['']
    # autocomplete_fields = ['occurrence']

    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)
        ct = ContentType.objects.get_for_model(Occurrence)
        return qs.filter(content_type_id=ct.id)


class AttributeesInline(TabularInline):
    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.attributees.count():
            return 0
        return 1


class BitesInline(TabularInline):
    model = models.QuoteBite
    extra = 0


class QuoteAdmin(Admin):
    # form = QuoteForm
    list_display = [
        'pk',
        'bite',
        'detail_link',
        'attributee_html',
        'date_string',
        'citation_html',
        'tags_string'
    ]
    list_filter = [
        'verified',
        HasSourceFilter,
        HasMultipleCitationsFilter,
        HasTagsFilter,
        TopicFilter,
        AttributeeFilter,
        AttributeeCountFilter,
        # AttributeeClassificationFilter  # broken
        'attributees__classifications'
    ]
    search_fields = models.Quote.searchable_fields
    ordering = ('date',)
    autocomplete_fields = []
    readonly_fields = ['citation_html']
    inlines = [
        AttributeesInline,
        CitationsInline,
        OccurrencesInline,
        RelatedTopicsInline,
        BitesInline
    ]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('date', 'date_is_circa'):
            if fields and field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('tag_search/',
                 self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                 name='tag_search'),
            path('entity_search/',
                 self.admin_site.admin_view(EntitySearchView.as_view(model_admin=self)),
                 name='entity_search')
        ]
        return custom_urls + urls


admin_site.register(models.Quote, QuoteAdmin)
