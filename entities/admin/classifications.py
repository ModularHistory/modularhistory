from admin import admin_site, Admin
from .. import models


class ClassificationAdmin(Admin):
    list_display = ('name', 'aliases')
    search_fields = list_display
    ordering = ('name',)


admin_site.register(models.Classification, ClassificationAdmin)
