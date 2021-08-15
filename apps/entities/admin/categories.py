from apps.admin.model_admin import ExtendedModelAdmin, admin_site
from apps.entities import models

CATEGORY_NAME_FIELD = 'name'
ALIASES_FIELD = 'aliases'


class CategoryAdmin(ExtendedModelAdmin):
    """Admin for entity categories."""

    list_display = [
        'pk',
        CATEGORY_NAME_FIELD,
        'part_of_speech',
        ALIASES_FIELD,
        'weight',
    ]
    search_fields = [CATEGORY_NAME_FIELD, ALIASES_FIELD]
    list_editable = [CATEGORY_NAME_FIELD, 'part_of_speech', ALIASES_FIELD, 'weight']
    ordering = ['name']


admin_site.register(models.Category, CategoryAdmin)
