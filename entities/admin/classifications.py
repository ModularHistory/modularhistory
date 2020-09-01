from history.admin import admin_site, Admin
from .. import models


class ClassificationAdmin(Admin):
    list_display = ['pk', 'name', 'part_of_speech', 'aliases', 'weight']
    search_fields = ['name', 'aliases']
    list_editable = ['name', 'part_of_speech', 'aliases', 'weight']
    ordering = ('name',)


admin_site.register(models.Classification, ClassificationAdmin)
