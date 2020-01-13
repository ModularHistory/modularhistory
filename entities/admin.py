# from django.forms import ModelForm

from django.contrib.admin import TabularInline, StackedInline, SimpleListFilter

# from django_reverse_admin import ReverseModelAdmin
from admin import admin_site, Admin
from quotes.models import Quote
from occurrences.models import OccurrenceEntityInvolvement
from topics.models import (
    EntityTopicRelation,
    EntityFactRelation
)
from . import models


class QuotesInline(StackedInline):
    model = Quote
    extra = 1
    show_change_link = True


class ImagesInline(TabularInline):
    model = models.Entity.images.through
    extra = 1


class TopicsInline(TabularInline):
    model = EntityTopicRelation
    extra = 1


class OccurrencesInline(TabularInline):
    model = OccurrenceEntityInvolvement
    extra = 1


class FactsInline(TabularInline):
    model = EntityFactRelation
    extra = 1


class AffiliationsInline(TabularInline):
    model = models.Affiliation
    extra = 1
    show_change_link = True


# class EntityAdmin(ReverseModelAdmin, Admin):
#     inlines = [QuotesInline, ImagesInline]
#     inline_type = 'tabular'


class HasQuotesFilter(SimpleListFilter):
    title = 'has quotes'
    parameter_name = 'has_quotes'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.exclude(quotes=None)
        elif value == 'No':
            return queryset.filter(quotes=None)
        return queryset


class EntityAdmin(Admin):
    list_display = ('name', 'description__truncated', 'birth_date', 'death_date', 'aliases')
    list_filter = ('is_living', HasQuotesFilter)
    search_fields = models.Entity.searchable_fields
    ordering = ('name', 'birth_date',)
    inlines = [
        QuotesInline, ImagesInline, AffiliationsInline,
        TopicsInline,
        FactsInline, OccurrencesInline
    ]


class OccupationAdmin(Admin):
    list_display = ('name', 'description', 'classification')
    list_filter = ('classification',)
    search_fields = list_display
    ordering = ('classification', 'name')


# admin_site.register(models.Entity, EntityAdmin)
admin_site.register(models.Person, EntityAdmin)
admin_site.register(models.Organization, EntityAdmin)
# admin_site.register(models.Affiliation, EntityAdmin)
admin_site.register(models.Occupation, OccupationAdmin)
admin_site.register(models.OccupationClassification, Admin)
admin_site.register(models.Role, Admin)
