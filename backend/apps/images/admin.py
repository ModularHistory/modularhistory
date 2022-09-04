from typing import TYPE_CHECKING

from django.db.models.aggregates import Count
from image_cropping import ImageCroppingMixin

from apps.admin import ExtendedModelAdmin, TabularInline, admin_site
from apps.admin.list_filters.boolean_filters import BooleanListFilter
from apps.entities.admin.filters import EntityAutocompleteFilter
from apps.entities.models.entity import Entity
from apps.images.models.image import Image
from apps.images.models.video import Video
from apps.search.admin import SearchableModelAdmin

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django.http import HttpRequest


class EntityFilter(EntityAutocompleteFilter):
    """Autocomplete filter for depicted entities."""

    title = 'entity'
    field_name = 'entity_set'


class EntitiesInline(TabularInline):
    """Inline admin for entities (in image admin)."""

    model = Entity.images.through
    verbose_name = 'entity'
    verbose_name_plural = 'entities'
    autocomplete_fields = ['content_object']


class ImageAdmin(ImageCroppingMixin, SearchableModelAdmin):
    """Admin for images."""

    list_display = [
        'admin_image_element',
        'detail_link',
        'caption',
        'provider',
        'date_string',
    ]
    list_filter = [EntityFilter]
    inlines = [EntitiesInline]
    search_fields = Image.searchable_fields
    readonly_fields = ['height', 'width', 'urls']

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page
    list_per_page = 10


class AbstractImagesInline(TabularInline):
    """Abstract base inline for images."""

    model: type['Model']

    autocomplete_fields = ['image']
    readonly_fields = ['admin_image_element']
    verbose_name = 'image'
    verbose_name_plural = 'images'

    extra = 0

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def admin_image_element(self, instance: 'Model'):
        """Return an inline image's admin image element."""
        return instance.image.admin_image_element


class HasMultipleImagesFilter(BooleanListFilter):
    """Filter for whether a model instance has multiple image relations."""

    title = 'has multiple images'
    parameter_name = 'has_multiple_images'

    def queryset(self, request: 'HttpRequest', queryset: 'QuerySet') -> 'QuerySet':
        """Return the filtered queryset."""
        queryset = queryset.annotate(citation_count=Count('images'))
        if self.value() == 'Yes':
            return queryset.exclude(citation_count__lt=2)
        if self.value() == 'No':
            return queryset.filter(citation_count__gte=2)


class VideoAdmin(ExtendedModelAdmin):
    """Admin for videos."""

    list_display = ['title', 'url']
    search_fields = ['title']
    readonly_fields = ['duration']


admin_site.register(Image, ImageAdmin)
admin_site.register(Video, VideoAdmin)
