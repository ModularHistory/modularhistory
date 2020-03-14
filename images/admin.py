from django.contrib.admin import TabularInline

from image_cropping import ImageCroppingMixin
from admin import admin_site, Admin
from entities.models import EntityImage
from occurrences.models import OccurrenceImage
from .models import Image, Video


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


class ImageAdmin(ImageCroppingMixin, Admin):
    list_display = [
        'admin_image_element',
        'detail_link',
        'caption',
        'provider',
        'date_string'
    ]
    inlines = [EntitiesInline, OccurrencesInline]
    search_fields = Image.searchable_fields
    readonly_fields = ['height', 'width']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for field_name in ('date_is_circa', 'date', 'type', 'image', 'hidden', 'verified'):
            if field_name in fields:
                fields.remove(field_name)
                fields.insert(0, field_name)
        # for field_name in ('position', 'page_number', 'end_page_number', 'notes'):
        #     if field_name in fields:
        #         fields.remove(field_name)
        #         fields.append(field_name)
        return fields


class VideoAdmin(Admin):
    list_display = ['title', 'link']
    search_fields = ['title']
    readonly_fields = ['duration']


admin_site.register(Image, ImageAdmin)
admin_site.register(Video, VideoAdmin)
