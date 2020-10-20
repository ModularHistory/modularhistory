from entities import models
from admin.model_admin import admin_site, ModelAdmin

CATEGORY_NAME_FIELD = 'name'
ALIASES_FIELD = 'aliases'


class CategoryAdmin(ModelAdmin):
    """Admin for entity categories."""

    list_display = ['pk', CATEGORY_NAME_FIELD, 'part_of_speech', ALIASES_FIELD, 'weight']
    search_fields = [CATEGORY_NAME_FIELD, ALIASES_FIELD]
    list_editable = [CATEGORY_NAME_FIELD, 'part_of_speech', ALIASES_FIELD, 'weight']
    ordering = ['name']


admin_site.register(models.Category, CategoryAdmin)
