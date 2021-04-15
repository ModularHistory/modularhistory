from apps.admin import ModelAdmin, TabularInline, admin_site
from apps.admin.list_filters import AutocompleteFilter
from apps.places import models
from apps.places.forms import PlaceForm


class LocationInline(TabularInline):
    """Inline admin for a location's parent location."""

    model = models.Place
    autocomplete_fields = [model.FieldNames.location]


class LocationFilter(AutocompleteFilter):
    """List filter for filtering locations by parent location."""

    title = 'location'
    field_name = models.Place.FieldNames.location


class LocationAdmin(ModelAdmin):
    """Admin for locations."""

    model = models.Place
    list_display = [model.FieldNames.name, 'string']
    list_filter = [LocationFilter]
    search_fields = [model.FieldNames.name]
    ordering = [
        model.FieldNames.name,
        f'{model.FieldNames.location}__{model.FieldNames.name}',
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
