from django.contrib import admin

from .models import (Location, City, County, State, Region, Country, Continent)

admin.site.register(Location)
admin.site.register(City)
admin.site.register(County)
admin.site.register(State)
admin.site.register(Region)
admin.site.register(Country)
admin.site.register(Continent)
