from image_cropping import ImageCroppingMixin

from admin import ModelAdmin, TabularInline, admin_site
from entities.models import EntityImage
from images.models import Image, Video
from occurrences.models import OccurrenceImage


class EntitiesInline(TabularInline):
    """Inline admin for entities (in image admin)."""

    model = EntityImage
    verbose_name = 'entity'
    extra = 1
    autocomplete_fields = ['entity']


class OccurrencesInline(TabularInline):
    """Inline admin for occurrences (in image admin)."""

    model = OccurrenceImage
    verbose_name = 'occurrence'
    extra = 1
    autocomplete_fields = ['occurrence']


class ImageAdmin(ImageCroppingMixin, ModelAdmin):
    """Admin for images."""

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

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10

    def get_fields(self, request, model_instance=None):
        """Returns reordered fields to be displayed in the admin."""
        fields = super().get_fields(request, model_instance)
        for field_name in ('date_is_circa', 'date', 'type', 'image', 'hidden', 'verified'):
            if field_name in fields:
                fields.remove(field_name)
                fields.insert(0, field_name)
        # for field_name in ('position', 'page_number', 'end_page_number', 'notes'):
        #     if field_name in fields:
        #         fields.remove(field_name)
        #         fields.append(field_name)
        return fields


class VideoAdmin(ModelAdmin):
    """Admin for videos."""

    list_display = ['title', 'url']
    search_fields = ['title']
    readonly_fields = ['duration']


admin_site.register(Image, ImageAdmin)
admin_site.register(Video, VideoAdmin)
