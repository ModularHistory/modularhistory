from django.contrib.admin import TabularInline

# from taggit_labels.widgets import LabelWidget
# from taggit.forms import TagField
from admin import admin_site, Admin
from entities.models import EntityImage
from occurrences.models import OccurrenceImage
from .models import Image


class EntitiesInline(TabularInline):
    model = EntityImage
    verbose_name = 'entity'
    extra = 1
    autocomplete_fields = ['entity']


class OccurrencesInline(TabularInline):
    model = OccurrenceImage
    verbose_name = 'occurrence'
    extra = 1
    autocomplete_fields = ['occurrence']


class ImageAdmin(Admin):
    list_display = ('admin_image_element', 'description', 'provider', 'date', 'year', )
    inlines = [EntitiesInline, OccurrencesInline]
    search_fields = Image.searchable_fields


admin_site.register(Image, ImageAdmin)
