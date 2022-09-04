"""Admin for the quotes app."""

from typing import TYPE_CHECKING

from rangefilter.filters import DateRangeFilter

from apps.admin.admin_site import admin_site
from apps.entities.admin.inlines import AbstractRelatedEntitiesInline
from apps.quotes import models
from apps.quotes.admin.filters import (
    AttributeeCategoryFilter,
    AttributeeCountFilter,
    AttributeeFilter,
)
from apps.quotes.admin.inlines import AttributeesInline
from apps.quotes.admin.related_quotes_inline import AbstractRelatedQuotesInline
from apps.search.admin import SearchableModelAdmin
from apps.sources.admin.citations import AbstractSourcesInline
from apps.sources.admin.filters.simple_filters import (
    HasMultipleSourcesFilter,
    HasSourceFilter,
)
from apps.topics.admin.filter import TopicFilter
from apps.topics.admin.tags import AbstractTagsInline, HasTagsFilter

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest


class SourcesInline(AbstractSourcesInline):
    """Inline admin for a quote's sources."""

    model = models.Quote.sources.through


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for a quote's related entities."""

    model = models.Quote.related_entities.through


class RelatedQuotesInline(AbstractRelatedQuotesInline):
    """Inline admin for a quote's related quotes."""

    model = models.Quote.related_quotes.through
    fk_name = 'content_object'


class TagsInline(AbstractTagsInline):
    """Inline admin for a quote's related entities."""

    model = models.Quote.tags.through


class QuoteAdmin(SearchableModelAdmin):
    """Model admin for quotes."""

    model = models.Quote

    exclude = SearchableModelAdmin.exclude + [
        'related_entities',
        # 'related_quotes',
    ]
    inlines = [
        AttributeesInline,
        SourcesInline,
        RelatedQuotesInline,
        RelatedEntitiesInline,
        TagsInline,
    ]
    list_display = [
        'title',
        'bite',
        'escaped_attributee_html',
        'date_string',
        'tags_string',
        'slug',
    ]
    list_filter = [
        'verified',
        HasSourceFilter,
        HasMultipleSourcesFilter,
        HasTagsFilter,
        TopicFilter,
        AttributeeFilter,
        AttributeeCategoryFilter,
        AttributeeCountFilter,
        ('date', DateRangeFilter),
    ]
    ordering = ['date']
    readonly_fields = SearchableModelAdmin.readonly_fields + [
        'attributee_html',
        'citation_html',
    ]
    search_fields = models.Quote.searchable_fields

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10

    def get_queryset(self, request: 'HttpRequest') -> 'QuerySet[models.Quote]':
        """
        Return the queryset of quotes to be displayed in the admin.

        https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset
        """
        qs = models.Quote.objects.prefetch_related('attributees', 'tags')
        ordering = self.get_ordering(request)
        if ordering and ordering != models.Quote._meta.ordering:
            qs = qs.order_by(*ordering)
        return qs


admin_site.register(models.Quote, QuoteAdmin)
