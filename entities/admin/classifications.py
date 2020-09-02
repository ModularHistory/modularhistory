from entities import models
from history.admin import admin_site, Admin


class EntityClassAdmin(Admin):
    """TODO: add docstring."""

    list_display = ['pk', 'name', 'part_of_speech', 'aliases', 'weight']
    search_fields = ['name', 'aliases']
    list_editable = ['name', 'part_of_speech', 'aliases', 'weight']
    ordering = ('name',)


admin_site.register(models.EntityClass, EntityClassAdmin)
admin_site.register(models.entity_class.Classification, EntityClassAdmin)
