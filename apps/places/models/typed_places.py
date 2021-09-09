
from apps.places.models.base import Place


class Venue(Place):
    """A specific place where something happens (e.g., a university)."""

    class Meta:
        """Meta options for Venue."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options


class City(Place):
    """A city."""

    class Meta:
        """Meta options for City."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Cities'


class County(Place):
    """A county."""

    class Meta:
        """Meta options for County."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Counties'


class State(Place):
    """A state."""

    class Meta:
        """Meta options for State."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'States'


class Region(Place):
    """A region."""

    class Meta:
        """Meta options for Region."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Regions'


class Country(Place):
    """A country."""

    class Meta:
        """Meta options for Country."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Countries'


class Continent(Place):
    """A continent."""

    class Meta:
        """Meta options for Continent."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Continents'
