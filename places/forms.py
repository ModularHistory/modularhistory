from django.forms import ModelForm

from .models import Place, Continent, Country, Region, State, County, City, Venue


class PlaceForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Place
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = self.instance.type


class ContinentForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Continent
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.continent'


class CountryForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Country
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.country'


class RegionForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Region
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.region'


class StateForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = State
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.state'


class CountyForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = County
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.county'


class CityForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = City
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.city'


class VenueForm(ModelForm):
    """TODO: add docstring."""

    class Meta:
        model = Venue
        exclude = []

    def __init__(self, *args, **kwargs):
        """TODO: add docstring."""
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.venue'
