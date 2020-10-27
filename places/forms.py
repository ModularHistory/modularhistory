from typing import List, Optional

from django.forms import ModelForm

from places.models import City, Continent, Country, County, Place, Region, State, Venue


class _PlaceForm(ModelForm):
    """Abstract place form."""

    type: Optional[str] = None  # noqa: WPS125

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = self.type or self.instance.type


class PlaceForm(_PlaceForm):
    """Form for place admin."""

    class Meta:
        model = Place
        exclude: List[str] = []


class ContinentForm(_PlaceForm):
    """Form for continent admin."""

    type = 'places.continent'  # noqa: WPS125

    class Meta:
        model = Continent
        exclude: List[str] = []


class CountryForm(_PlaceForm):
    """Form for country admin."""

    type = 'places.country'  # noqa: WPS125

    class Meta:
        model = Country
        exclude: List[str] = []


class RegionForm(ModelForm):
    """Form for region admin."""

    type = 'places.region'  # noqa: WPS125

    class Meta:
        model = Region
        exclude: List[str] = []


class StateForm(ModelForm):
    """Form for state admin."""

    type = 'places.state'  # noqa: WPS125

    class Meta:
        model = State
        exclude: List[str] = []


class CountyForm(ModelForm):
    """Form for county admin."""

    type = 'places.county'  # noqa: WPS125

    class Meta:
        model = County
        exclude: List[str] = []


class CityForm(ModelForm):
    """Form for city admin."""

    type = 'places.city'  # noqa: WPS125

    class Meta:
        model = City
        exclude: List[str] = []


class VenueForm(ModelForm):
    """Form for venue admin."""

    type = 'places.venue'  # noqa: WPS125

    class Meta:
        model = Venue
        exclude: List[str] = []
