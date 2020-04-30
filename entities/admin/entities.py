from admin import admin_site, Admin, TabularInline
from occurrences.models import OccurrenceEntityInvolvement
from quotes.models import Quote
from topics.models import EntityFactRelation
from quotes.admin import RelatedQuotesInline
from .admin_filters import ClassificationFilter, HasImageFilter, HasQuotesFilter
from .affiliations import RolesInline
from .. import models
from ..forms import (
    PersonForm, GroupForm,
    OrganizationForm, IdeaForm
)


class QuotesInline(TabularInline):
    model = Quote.attributees.through
    extra = 0
    show_change_link = True
    autocomplete_fields = ['quote']

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
    inlines = [RolesInline]


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
        RelatedQuotesInline
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


class IdeaAdmin(Admin):
    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Entity, EntityAdmin)
admin_site.register(models.Person, PersonAdmin)
admin_site.register(models.Group, GroupAdmin)
admin_site.register(models.Organization, OrganizationAdmin)
