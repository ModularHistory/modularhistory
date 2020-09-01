from history.admin import admin_site, Admin, TabularInline
from .. import models


class RoleAdmin(Admin):
    search_fields = ['name']


class RolesInline(TabularInline):
    model = models.Affiliation.roles.through
    autocomplete_fields = ['role']
    extra = 0

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field in ('start_date', 'end_date'):
            if field in fields:
                fields.remove(field)
                fields.append(field)
        return fields


class AffiliationAdmin(Admin):
    list_display = ['entity', 'affiliated_entity', 'start_date', 'end_date']
    search_fields = list_display
    autocomplete_fields = ['entity', 'affiliated_entity']
    ordering = ('start_date', 'entity')
    inlines = [RolesInline]


admin_site.register(models.Affiliation, AffiliationAdmin)
admin_site.register(models.Role, RoleAdmin)
