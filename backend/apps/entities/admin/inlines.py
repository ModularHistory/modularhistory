from apps.admin import TabularInline
from apps.entities import models
from apps.images.admin import AbstractImagesInline
from apps.quotes.models.quote import Quote


class AbstractRelatedEntitiesInline(TabularInline):
    """Inline admin for related entities."""

    extra = 0
    show_change_link = True
    autocomplete_fields = ['entity']
    verbose_name = 'related entity'
    verbose_name_plural = 'related entities'


class RelatedEntitiesInline(AbstractRelatedEntitiesInline):
    """Inline admin for related entities."""

    model = models.Entity


class QuotesInline(TabularInline):
    """Inline admin for quotes."""

    model = Quote.attributees.through
    extra = 0
    show_change_link = True
    autocomplete_fields = ['quote']

    def get_fields(self, *args, **kwargs):
        """Return reordered fields to be displayed in the admin."""
        fields = list(super().get_fields(*args, **kwargs))
        for field in ('date_is_circa', 'date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class ImagesInline(AbstractImagesInline):
    """Inline admin for images."""

    model = models.Entity.images.through

    extra = 1


class CategorizationsInline(TabularInline):
    """Inline admin for categorizations."""

    model = models.Categorization
    extra = 1
    autocomplete_fields = ['category']
    readonly_fields = ['weight']
