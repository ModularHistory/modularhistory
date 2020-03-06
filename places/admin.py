from admin import admin_site, Admin, TabularInline
from . import models
from .forms import PlaceForm


class LocationInline(TabularInline):
    model = models.Place
    autocomplete_fields = ['location']


class LocationAdmin(Admin):
    list_display = ('name', 'location')
    list_filter = ('location',)
    search_fields = ('name',)
    ordering = ('name', 'location__name')
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
