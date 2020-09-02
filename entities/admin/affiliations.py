from entities import models
from history.admin import admin_site, Admin, TabularInline


class RoleAdmin(Admin):
    """TODO: add docstring."""

    search_fields = ['name']


class RolesInline(TabularInline):
    """TODO: add docstring."""

    model = models.Affiliation.roles.through
    autocomplete_fields = ['role']
    extra = 0

    def get_fields(self, request, obj=None):
        """TODO: add docstring."""
        fields = super().get_fields(request, obj)
        for field in ('start_date', 'end_date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class AffiliationAdmin(Admin):
    """TODO: add docstring."""

    list_display = ['entity', 'affiliated_entity', 'start_date', 'end_date']
    search_fields = list_display
    autocomplete_fields = ['entity', 'affiliated_entity']
    ordering = ('start_date', 'entity')
    inlines = [RolesInline]


admin_site.register(models.Affiliation, AffiliationAdmin)
admin_site.register(models.Role, RoleAdmin)
