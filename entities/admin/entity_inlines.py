from admin import TabularInline
from entities import models
from occurrences.models import OccurrenceEntityInvolvement
from quotes.models import Quote
from topics.models import EntityFactRelation


class QuotesInline(TabularInline):
    """TODO: add docstring."""

    model = Quote.attributees.through
    extra = 0
    show_change_link = True
    autocomplete_fields = ['quote']

    # def get_fields(self, request, obj=None):
    def get_fields(self, *args, **kwargs):
        """TODO: add docstring."""
        fields = super().get_fields(*args, **kwargs)
        for field in ('date_is_circa', 'date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class ImagesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Entity.images.through
    extra = 1
    autocomplete_fields = ['image']


class OccurrencesInline(TabularInline):
    """TODO: add docstring."""

    model = OccurrenceEntityInvolvement
    extra = 1
    autocomplete_fields = ['occurrence']


class FactsInline(TabularInline):
    """TODO: add docstring."""

    model = EntityFactRelation
    extra = 1
    autocomplete_fields = ['fact']


class CategorizationsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Categorization
    extra = 1
    autocomplete_fields = ['category']
    readonly_fields = ['weight']
