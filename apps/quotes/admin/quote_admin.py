"""Admin for the quotes app."""

from django.db.models.query import QuerySet

from apps.admin import admin_site
from apps.quotes import models
from apps.quotes.admin.quote_filters import (
    AttributeeCategoryFilter,
    AttributeeCountFilter,
    AttributeeFilter,
)
from apps.quotes.admin.quote_inlines import AttributeesInline, BitesInline
from apps.quotes.admin.related_quotes_inline import RelatedQuotesInline
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.citations import CitationsInline
from apps.sources.admin.filters.simple_filters import (
    HasMultipleCitationsFilter,
    HasSourceFilter,
)
from apps.topics.admin import HasTagsFilter, RelatedTopicsInline
from apps.topics.models.taggable_model import TopicFilter


class QuoteAdmin(SearchableModelAdmin):
    """Model admin for quotes."""

    model = models.Quote

    list_display = [
        'pk',
        'bite',
        'detail_link',
        'attributee_html',
        'date_string',
        'citation_html',
        'tags_string',
        'slug',
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
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        'attributee_html',
        'citation_html',
    ]
    inlines = [
        AttributeesInline,
        CitationsInline,
        RelatedQuotesInline,
        RelatedTopicsInline,
        BitesInline,
    ]

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    date_hierarchy = 'date'

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10

    def get_queryset(self, request) -> 'QuerySet[models.Quote]':
        """
        Return the queryset of quotes to be displayed in the admin.

        https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset
        """
        qs = models.Quote.objects.prefetch_related('attributees', 'tags__topic')
        ordering = self.get_ordering(request)
        if ordering and ordering != models.Quote.get_meta().ordering:
            qs = qs.order_by(*ordering)
        return qs


admin_site.register(models.Quote, QuoteAdmin)
