from apps.places.models.base import Place


class Venue(Place):
    """A specific place where something happens (e.g., a university)."""


class City(Place):
    """A city."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        verbose_name_plural = 'Cities'


class County(Place):
    """A county."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        verbose_name_plural = 'Counties'


class State(Place):
    """A state within a country."""


class AdministrativeDivision(Place):
    """An administrative division within a country; e.g., England within the UK."""


class Country(Place):
    """A country or nation."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        verbose_name_plural = 'Countries'


class Region(Place):
    """A super-country region within a continent."""


class Continent(Place):
    """A continent."""
