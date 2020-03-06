from django.forms import ModelForm

from .models import Place, Continent, Country, Region, State, County, City, Venue


class PlaceForm(ModelForm):
    class Meta:
        model = Place
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = self.instance.type


class ContinentForm(ModelForm):
    class Meta:
        model = Continent
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.continent'


class CountryForm(ModelForm):
    class Meta:
        model = Country
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.country'


class RegionForm(ModelForm):
    class Meta:
        model = Region
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.region'


class StateForm(ModelForm):
    class Meta:
        model = State
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.state'


class CountyForm(ModelForm):
    class Meta:
        model = County
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.county'


class CityForm(ModelForm):
    class Meta:
        model = City
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.city'


class VenueForm(ModelForm):
    class Meta:
        model = Venue
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['type'] = 'places.venue'
