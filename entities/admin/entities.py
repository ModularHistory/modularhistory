from entities import models
from entities.admin.admin_filters import (
    CategoriesFilter,
    HasImageFilter,
    HasQuotesFilter,
)
from entities.admin.affiliations import AffiliationsInline
from entities.admin.entity_inlines import (
    CategorizationsInline,
    QuotesInline,
    ImagesInline,
    OccurrencesInline,
    FactsInline,
)
from entities.forms import PersonForm, GroupForm, OrganizationForm
from admin.model_admin import admin_site, ModelAdmin
from quotes.admin import RelatedQuotesInline


class EntityAdmin(ModelAdmin):
    """Admin for entities."""

    model = models.Entity
    list_display = [
        'name',
        'truncated_description',
        'birth_date',
        'death_date',
        'aliases',
        'id',
    ]
    list_filter = [HasQuotesFilter, HasImageFilter, CategoriesFilter]
    # list_editable = []
    inlines = [
        ImagesInline,
        CategorizationsInline,
        FactsInline,
        AffiliationsInline,
        OccurrencesInline,
        QuotesInline,
        RelatedQuotesInline,
    ]
    ordering = ['name', 'birth_date']
    readonly_fields = ['computations']
    search_fields = ['name', 'aliases']


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


admin_site.register(models.Entity, EntityAdmin)
admin_site.register(models.Person, PersonAdmin)
admin_site.register(models.Group, GroupAdmin)
admin_site.register(models.Organization, OrganizationAdmin)
