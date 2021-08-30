from apps.admin.model_admin import admin_site
from apps.entities import models
from apps.entities.admin.affiliations import AffiliationsInline
from apps.entities.admin.filters import (
    CategoriesFilter,
    EntityTypeFilter,
    HasImageFilter,
    HasQuotesFilter,
)
from apps.entities.admin.inlines import CategorizationsInline, ImagesInline, QuotesInline
from apps.entities.forms import DeityForm, GroupForm, OrganizationForm, PersonForm
from apps.quotes.admin.related_quotes_inline import AbstractRelatedQuotesInline
from apps.search.admin import SearchableModelAdmin


class RelatedQuotesInline(AbstractRelatedQuotesInline):
    """Inline admin for an entity's related quotes."""

    model = models.Entity.related_quotes.through


class EntityAdmin(SearchableModelAdmin):
    """Admin for entities."""

    model = models.Entity

    exclude = SearchableModelAdmin.exclude + [
        'related_entities',
        'related_quotes',
    ]
    inlines = [
        ImagesInline,
        CategorizationsInline,
        AffiliationsInline,
        QuotesInline,
        RelatedQuotesInline,
    ]
    list_display = [
        'name',
        'truncated_description',
        'birth_date',
        'death_date',
        'aliases',
        'type',
    ]
    list_filter = [
        'verified',
        HasQuotesFilter,
        HasImageFilter,
        CategoriesFilter,
        EntityTypeFilter,
    ]
    ordering = ['name', 'birth_date']
    readonly_fields = SearchableModelAdmin.readonly_fields
    search_fields = ['name', 'aliases']


class TypedEntityAdmin(EntityAdmin):
    """Base admin for typed entities."""

    list_display = [
        'name',
        'truncated_description',
        'birth_date',
        'death_date',
        'aliases',
    ]
    list_filter = [HasQuotesFilter, HasImageFilter, CategoriesFilter]


class PersonAdmin(TypedEntityAdmin):
    """Admin for persons."""

    model = models.Person
    exclude = [*TypedEntityAdmin.exclude]
    form = PersonForm
    add_form = PersonForm


class DeityAdmin(TypedEntityAdmin):
    """Admin for persons."""

    model = models.Deity
    exclude = [*TypedEntityAdmin.exclude]
    form = DeityForm
    add_form = DeityForm


class GroupAdmin(TypedEntityAdmin):
    """Admin for groups."""

    model = models.Group
    exclude = [*TypedEntityAdmin.exclude]
    form = GroupForm
    add_form = GroupForm


class OrganizationAdmin(TypedEntityAdmin):
    """Admin for organizations."""

    model = models.Person
    form = OrganizationForm
    add_form = OrganizationForm


admin_site.register(models.Entity, EntityAdmin)
admin_site.register(models.Person, PersonAdmin)
admin_site.register(models.Group, GroupAdmin)
admin_site.register(models.Organization, OrganizationAdmin)
