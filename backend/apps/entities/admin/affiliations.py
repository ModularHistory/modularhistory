from apps.admin import ExtendedModelAdmin, TabularInline, admin_site
from apps.entities import models


class RoleAdmin(ExtendedModelAdmin):
    """Admin for roles."""

    search_fields = ['name']


class RolesInline(TabularInline):
    """Inline admin for roles."""

    model = models.Affiliation.roles.through
    autocomplete_fields = ['role']
    extra = 0

    def get_fields(self, *args, **kwargs):
        """Return reordered fields to be displayed in the admin."""
        fields = list(super().get_fields(*args, **kwargs))
        for field in ('start_date', 'end_date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class AffiliationAdmin(ExtendedModelAdmin):
    """Admin for affiliations."""

    list_display = ['entity', 'affiliated_entity', 'start_date', 'end_date']
    search_fields = list_display
    autocomplete_fields = ['entity', 'affiliated_entity']
    ordering = ['start_date', 'entity']
    inlines = [RolesInline]


class AffiliationsInline(TabularInline):
    """Inline admin for affiliations."""

    model = models.Affiliation
    fk_name = 'affiliated_entity'
    autocomplete_fields = AffiliationAdmin.autocomplete_fields
    inlines = AffiliationAdmin.inlines
    show_change_link = True
    extra = 1


admin_site.register(models.Affiliation, AffiliationAdmin)
admin_site.register(models.Role, RoleAdmin)
