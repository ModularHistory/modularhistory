from entities import models
from entities.admin.admin_filters import CategoriesFilter, HasImageFilter, HasQuotesFilter
from entities.admin.affiliations import RolesInline
from entities.forms import (
    PersonForm, GroupForm,
    OrganizationForm, IdeaForm
)
from history.admin import admin_site, Admin, TabularInline
from occurrences.models import OccurrenceEntityInvolvement
from quotes.admin import RelatedQuotesInline
from quotes.models import Quote
from topics.models import EntityFactRelation


class QuotesInline(TabularInline):
    """TODO: add docstring."""

    model = Quote.attributees.through
    extra = 0
    show_change_link = True
    autocomplete_fields = ['quote']

    def get_fields(self, request, obj=None):
        """TODO: add docstring."""
        fields = super().get_fields(request, obj)
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


class CategorizationsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Categorization
    extra = 1
    autocomplete_fields = ['category']
    readonly_fields = ['weight']


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


class AffiliationsInline(TabularInline):
    """TODO: add docstring."""

    model = models.Affiliation
    fk_name = 'affiliated_entity'
    extra = 1
    show_change_link = True
    autocomplete_fields = ['affiliated_entity']
    inlines = [RolesInline]


class EntityAdmin(Admin):
    """TODO: add docstring."""

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
        CategoriesFilter
    ]
    search_fields = ['name', 'aliases']
    ordering = ['name', 'birth_date']
    # list_editable = []
    inlines = [
        ImagesInline,
        CategorizationsInline,
        FactsInline,
        AffiliationsInline,
        OccurrencesInline,
        QuotesInline,
        RelatedQuotesInline
    ]


class PersonAdmin(EntityAdmin):
    """TODO: add docstring."""

    model = models.Person
    exclude = ['parent_organization']
    form = PersonForm
    add_form = PersonForm


class GroupAdmin(EntityAdmin):
    """TODO: add docstring."""

    model = models.Group
    exclude = ['parent_organization']
    form = GroupForm
    add_form = GroupForm


class OrganizationAdmin(EntityAdmin):
    """TODO: add docstring."""

    model = models.Person
    form = OrganizationForm
    add_form = OrganizationForm


class IdeaAdmin(Admin):
    """TODO: add docstring."""

    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Entity, EntityAdmin)
admin_site.register(models.Person, PersonAdmin)
admin_site.register(models.Group, GroupAdmin)
admin_site.register(models.Organization, OrganizationAdmin)
