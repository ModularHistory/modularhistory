from typing import Type

from django.db.models.aggregates import Count
from image_cropping import ImageCroppingMixin

from apps.admin import ModelAdmin, TabularInline, admin_site
from apps.admin.list_filters.boolean_filters import BooleanListFilter
from apps.entities.models.entity_image import EntityImage
from apps.images.models.image import Image
from apps.images.models.video import Video
from apps.occurrences.models import OccurrenceImage
from apps.search.admin import SearchableModelAdmin


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


class ImageAdmin(ImageCroppingMixin, SearchableModelAdmin):
    """Admin for images."""

    list_display = [
        'admin_image_element',
        'detail_link',
        'caption',
        'provider',
        'date_string',
    ]
    inlines = [EntitiesInline, OccurrencesInline]
    search_fields = Image.searchable_fields
    readonly_fields = ['height', 'width', 'urls', 'pretty_computations']

    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10


class AbstractImagesInline(TabularInline):
    """Abstract base inline for images."""

    model: Type

    autocomplete_fields = ['image']
    readonly_fields = ['key', 'image_pk']
    verbose_name = 'image'
    verbose_name_plural = 'images'

    extra = 0

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'


class HasMultipleImagesFilter(BooleanListFilter):
    """Filter for whether a model instance has multiple image relations."""

    title = 'has multiple images'
    parameter_name = 'has_multiple_images'

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        queryset = queryset.annotate(citation_count=Count('images'))
        if self.value() == 'Yes':
            return queryset.exclude(citation_count__lt=2)
        if self.value() == 'No':
            return queryset.filter(citation_count__gte=2)


class VideoAdmin(ModelAdmin):
    """Admin for videos."""

    list_display = ['title', 'url']
    search_fields = ['title']
    readonly_fields = ['duration']


admin_site.register(Image, ImageAdmin)
admin_site.register(Video, VideoAdmin)
