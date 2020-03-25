from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import SimpleListFilter

from admin import admin_site, Admin, StackedInline, TabularInline
from occurrences.models import OccurrenceEntityInvolvement
from quotes.models import Quote
from topics.models import EntityFactRelation
# from django.forms import ModelForm
# from django_reverse_admin import ReverseModelAdmin
from . import models
from .forms import (
    PersonForm, GroupForm,
    OrganizationForm, IdeaForm
)


class ClassificationFilter(AutocompleteFilter):
    title = 'Classification'
    field_name = 'classifications'


class QuotesInline(TabularInline):
    model = Quote
    extra = 0
    show_change_link = True
    fields = ['verified', 'hidden']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field in ('date_is_circa', 'date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class ImagesInline(TabularInline):
    model = models.Entity.images.through
    extra = 1
    autocomplete_fields = ['image']


class ClassificationsInline(TabularInline):
    model = models.EntityClassification
    extra = 1
    autocomplete_fields = ['classification']
    readonly_fields = ['weight']


class OccurrencesInline(TabularInline):
    model = OccurrenceEntityInvolvement
    extra = 1
    autocomplete_fields = ['occurrence']


class FactsInline(TabularInline):
    model = EntityFactRelation
    extra = 1
    autocomplete_fields = ['fact']


class AffiliationsInline(TabularInline):
    model = models.Affiliation
    fk_name = 'affiliated_entity'
    extra = 1
    show_change_link = True
    autocomplete_fields = ['affiliated_entity']


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


class HasImageFilter(SimpleListFilter):
    title = 'has image'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.exclude(images=None)
        elif value == 'No':
            return queryset.filter(images=None)
        return queryset


class EntityAdmin(Admin):
    model = models.Entity
    list_display = [
        'name',
        'description__truncated',
        'birth_date',
        'death_date',
        'aliases',
        'id'
    ]
    list_filter = [
        HasQuotesFilter,
        HasImageFilter,
        ClassificationFilter
    ]
    search_fields = ['name', 'aliases']
    ordering = ['name', 'birth_date']
    # list_editable = []
    inlines = [
        ImagesInline,
        ClassificationsInline,
        FactsInline,
        AffiliationsInline,
        OccurrencesInline,
        QuotesInline,
    ]


class PersonAdmin(EntityAdmin):
    model = models.Person
    exclude = ['parent_organization']
    form = PersonForm
    add_form = PersonForm


class GroupAdmin(EntityAdmin):
    model = models.Group
    exclude = ['parent_organization']
    form = GroupForm
    add_form = GroupForm


class OrganizationAdmin(EntityAdmin):
    model = models.Person
    form = OrganizationForm
    add_form = OrganizationForm


class ClassificationAdmin(Admin):
    list_display = ('name', 'aliases')
    search_fields = list_display
    ordering = ('name',)


class IdeaAdmin(Admin):
    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Entity, EntityAdmin)
admin_site.register(models.Person, PersonAdmin)
admin_site.register(models.Group, GroupAdmin)
admin_site.register(models.Organization, OrganizationAdmin)
# admin_site.register(models.Affiliation, EntityAdmin)
admin_site.register(models.Classification, ClassificationAdmin)
admin_site.register(models.Role, Admin)
admin_site.register(models.Idea, IdeaAdmin)
