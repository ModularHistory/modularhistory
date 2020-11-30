from admin import TabularInline
from apps.entities import models
from apps.occurrences.models import OccurrenceEntityInvolvement
from apps.postulations.models import EntityFactRelation
from apps.quotes.models import Quote


class QuotesInline(TabularInline):
    """Inline admin for quotes."""

    model = Quote.attributees.through
    extra = 0
    show_change_link = True
    autocomplete_fields = ['quote']

    def get_fields(self, *args, **kwargs):
        """Return reordered fields to be displayed in the admin."""
        fields = super().get_fields(*args, **kwargs)
        for field in ('date_is_circa', 'date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class ImagesInline(TabularInline):
    """Inline admin for images."""

    model = models.Entity.images.through
    extra = 1
    autocomplete_fields = ['image']


class OccurrencesInline(TabularInline):
    """Inline admin for occurrences."""

    model = OccurrenceEntityInvolvement
    extra = 1
    autocomplete_fields = ['occurrence']


class FactsInline(TabularInline):
    """Inline admin for postulations."""

    model = EntityFactRelation
    extra = 1
    autocomplete_fields = ['fact']


class CategorizationsInline(TabularInline):
    """Inline admin for categorizations."""

    model = models.Categorization
    extra = 1
    autocomplete_fields = ['category']
    readonly_fields = ['weight']
