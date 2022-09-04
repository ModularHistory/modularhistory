from django.db.models import Model

from apps.admin import ExtendedModelAdmin, TabularInline, admin_site
from apps.admin.list_filters import AutocompleteFilter
from apps.places import models
from apps.places.forms import PlaceForm


class AbstractLocationsInline(TabularInline):
    """Inline admin for an occurrence's locations."""

    model: type[Model]
    extra = 0
    autocomplete_fields = ['location']
    verbose_name = 'location'
    verbose_name_plural = 'locations'


class LocationInline(AbstractLocationsInline):
    """Inline admin for a location's parent location."""

    model = models.Place
    autocomplete_fields = ['location']


class LocationFilter(AutocompleteFilter):
    """List filter for filtering locations by parent location."""

    title = 'location'
    field_name = 'location'


class LocationAdmin(ExtendedModelAdmin):
    """Admin for locations."""

    model = models.Place
    list_display = ['name', 'string']
    list_filter = [LocationFilter]
    search_fields = ['name']
    ordering = [
        'name',
        'location__name',
    ]
    form = PlaceForm
    add_form = PlaceForm


admin_site.register(models.Place, LocationAdmin)
admin_site.register(models.Venue, LocationAdmin)
admin_site.register(models.City, LocationAdmin)
admin_site.register(models.County, LocationAdmin)
admin_site.register(models.State, LocationAdmin)
admin_site.register(models.Region, LocationAdmin)
admin_site.register(models.Country, LocationAdmin)
admin_site.register(models.Continent, LocationAdmin)
