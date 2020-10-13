"""Admin for the quotes app."""

from typing import Optional

from django.urls import path

from admin.admin import Admin, TabularInline, admin_site
from entities.views import EntityCategorySearchView, EntitySearchView
from modularhistory.models.taggable_model import TopicFilter
from quotes import models
from quotes.admin.filters import (
    AttributeeCategoryFilter,
    AttributeeCountFilter,
    AttributeeFilter,
    HasMultipleCitationsFilter,
    HasSourceFilter
)
from quotes.admin.related_quotes_inline import RelatedQuotesInline
from sources.admin.citations_admin import CitationsInline
from topics.admin import HasTagsFilter, RelatedTopicsInline
from topics.views import TagSearchView


class AttributeesInline(TabularInline):
    """TODO: add docstring."""

    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'

    def get_extra(self, request, obj: Optional[models.Quote] = None, **kwargs):
        """TODO: add docstring."""
        if obj and obj.attributees.count():
            return 0
        return 1


class BitesInline(TabularInline):
    """TODO: add docstring."""

    model = models.QuoteBite
    extra = 0


# TODO: try to get this reverse relationship working
# class OccurrencesInline(GenericTabularInline):
#     model = models.QuoteRelation
#     # readonly_fields = ['']
#     # autocomplete_fields = ['occurrence']
#     verbose_name = 'occurrence'
#     verbose_name_plural = 'occurrences'
#
#     def get_queryset(self, request):
#         # qs: QuerySet = super().get_queryset(request)
#         pk = re.search(r'/(\d+)/', request.path).group(1)
#         ct = ContentType.objects.get_for_model(Occurrence)
#         qs: QuerySet = models.QuoteRelation.objects.filter(
#             quote_id=pk,
#             content_type_id=ct.id
#         )
#         return qs.filter(content_type_id=ct.id)
#
#     def get_extra(self, request, obj=None, **kwargs):
#         if len(self.get_queryset(request)):
#             return 0
#         return 1


class QuoteAdmin(Admin):
    """TODO: add docstring."""

    model = models.Quote

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
        AttributeeCategoryFilter,
        AttributeeCountFilter,
    ]
    search_fields = models.Quote.searchable_fields
    ordering = ['date']
    # autocomplete_fields = []
    readonly_fields = ['citation_html']
    inlines = [
        AttributeesInline,
        CitationsInline,
        # OccurrencesInline,
        RelatedQuotesInline,
        RelatedTopicsInline,
        BitesInline
    ]

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10

    def get_fields(self, request, obj=None):
        """TODO: add docstring."""
        fields = list(super().get_fields(request, obj))
        for field_name in ('date', 'date_is_circa'):
            if fields and field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields

    def get_queryset(self, request):
        """
        https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset
        """
        qs = models.Quote.objects.prefetch_related(
            'attributees',  # 2353 -> 2261 queries
            'tags',  # 2261 -> 2184 queries
            # 'citations__source',  # 5840
            # 'citations',  # 5851
        )
        ordering = self.get_ordering(request)
        if ordering and ordering != models.Quote.get_meta().ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_urls(self):
        """TODO: add docstring."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'tag_search/',
                self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                name='tag_search'
            ),
            path(
                'entity_search/',
                self.admin_site.admin_view(EntitySearchView.as_view(model_admin=self)),
                name='entity_search'
            ),
            path(
                'entity_category_search/',
                self.admin_site.admin_view(EntityCategorySearchView.as_view(model_admin=self)),
                name='entity_category_search'
            )
        ]
        return custom_urls + urls


admin_site.register(models.Quote, QuoteAdmin)
