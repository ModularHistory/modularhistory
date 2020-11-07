"""Admin for the quotes app."""

from django.db.models.query import QuerySet

from admin import admin_site
from admin.searchable_model_admin import SearchableModelAdmin
from modularhistory.models.taggable_model import TopicFilter
from quotes import models
from quotes.admin.quote_filters import (
    AttributeeCategoryFilter,
    AttributeeCountFilter,
    AttributeeFilter,
    HasMultipleCitationsFilter,
    HasSourceFilter,
)
from quotes.admin.quote_inlines import AttributeesInline, BitesInline
from quotes.admin.related_quotes_inline import RelatedQuotesInline
from sources.admin.citation_admin import CitationsInline
from topics.admin import HasTagsFilter, RelatedTopicsInline


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
    readonly_fields = SearchableModelAdmin.readonly_fields + ['citation_html']
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

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        fields = list(super().get_fields(request, model_instance))
        for field_name in ('date', 'date_is_circa'):
            if fields and field_name in fields:
                fields.remove(field_name)
                fields.append(field_name)
        return fields

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
