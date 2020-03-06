from polymorphic.admin import (PolymorphicParentModelAdmin, PolymorphicChildModelAdmin,
                               StackedPolymorphicInline, PolymorphicInlineSupportMixin)

from admin import admin_site, Admin
from . import models


class LocationInline(StackedPolymorphicInline):
    model = models.Place
    autocomplete_fields = ['location']

    class VenueInline(StackedPolymorphicInline.Child):
        model = models.Venue

    class CityInline(StackedPolymorphicInline.Child):
        model = models.City

    class CountyInline(StackedPolymorphicInline.Child):
        model = models.County

    class StateInline(StackedPolymorphicInline.Child):
        model = models.State

    class RegionInline(StackedPolymorphicInline.Child):
        model = models.Region

    class CountryInline(StackedPolymorphicInline.Child):
        model = models.Country

    class ContinentInline(StackedPolymorphicInline.Child):
        model = models.Continent

    child_inlines = (
        VenueInline,
        CityInline,
        CountyInline,
        StateInline,
        RegionInline,
        CountryInline,
        ContinentInline
    )


class LocationAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, Admin):
    base_model = models.Place
    child_models = [
        models.Venue,
        models.City,
        models.County,
        models.State,
        models.Region,
        models.Country,
        models.Continent
    ]
    list_display = ('name', 'location')
    list_filter = ('location',)
    search_fields = ('name',)
    ordering = ('name', 'location__name')


class ChildModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Place
    inlines = [LocationInline]


admin_site.register(models.Venue, ChildModelAdmin)
admin_site.register(models.City, ChildModelAdmin)
admin_site.register(models.County, ChildModelAdmin)
admin_site.register(models.State, ChildModelAdmin)
admin_site.register(models.Region, ChildModelAdmin)
admin_site.register(models.Country, ChildModelAdmin)
admin_site.register(models.Continent, ChildModelAdmin)
admin_site.register(models.Place, LocationAdmin)
