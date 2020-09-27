from typing import List, Optional

from django.forms import ModelForm

from .models import Place, Continent, Country, Region, State, County, City, Venue


class _PlaceForm(ModelForm):
    """TODO: add docstring."""

    type: Optional[str] = None

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = self.type or self.instance.type


class PlaceForm(_PlaceForm):
    """TODO: add docstring."""

    class Meta:
        model = Place
        exclude: List[str] = []


class ContinentForm(_PlaceForm):
    """TODO: add docstring."""

    type = 'places.continent'

    class Meta:
        model = Continent
        exclude: List[str] = []


class CountryForm(_PlaceForm):
    """TODO: add docstring."""

    type = 'places.country'

    class Meta:
        model = Country
        exclude: List[str] = []


class RegionForm(ModelForm):
    """TODO: add docstring."""

    type = 'places.region'

    class Meta:
        model = Region
        exclude: List[str] = []


class StateForm(ModelForm):
    """TODO: add docstring."""

    type = 'places.state'

    class Meta:
        model = State
        exclude: List[str] = []


class CountyForm(ModelForm):
    """TODO: add docstring."""

    type = 'places.county'

    class Meta:
        model = County
        exclude: List[str] = []


class CityForm(ModelForm):
    """TODO: add docstring."""

    type = 'places.city'

    class Meta:
        model = City
        exclude: List[str] = []


class VenueForm(ModelForm):
    """TODO: add docstring."""

    type = 'places.venue'

    class Meta:
        model = Venue
        exclude: List[str] = []
