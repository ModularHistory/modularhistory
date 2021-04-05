"""Model classes for spoken sources."""

from apps.places.models import Venue
from apps.sources.models.source import Source
from modularhistory.fields import ExtraField

JSON_FIELD_NAME = 'extra'


class SpokenSource(Source):
    """Spoken words (e.g., a speech, lecture, or discourse) as a source."""

    audience = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        type_label = str(self.type_label)
        delivery_string = f'{type_label}'
        audience, location, date = self.audience, self.location, self.date
        if any([audience, location, date]):
            if type_label != 'statement':
                delivery_string = f'{type_label} delivered'
            if audience or location:
                if audience:
                    delivery_string = f'{delivery_string} to {audience}'
                if location:
                    preposition = (
                        location.preposition if isinstance(location, Venue) else 'in'
                    )
                    delivery_string = (
                        f'{delivery_string} {preposition} {location.string}'
                    )
                if date:
                    delivery_string = f'{delivery_string}, {self.date_string}'
            elif date:
                if date.month_is_known:
                    delivery_string = f'{delivery_string} {self.date_string}'
                else:
                    delivery_string = f'{delivery_string} in {self.date_string}'
        # Build full string
        components = [
            self.attributee_html,
            f'"{self.linked_title}"' if self.title else '',
            delivery_string,
        ]
        return self.components_to_html(components)

    @property
    def type_label(self) -> str:
        """Type label used in strings; e.g., 'speech', 'discourse', 'lecture', etc."""
        raise NotImplementedError


class Speech(SpokenSource):
    """A speech as a source."""

    type_label = 'speech'

    class Meta:
        """Meta options for the Speech model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Speeches'


class Address(SpokenSource):
    """An address as a source."""

    type_label = 'address'

    class Meta:
        """Meta options for the Address model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Addresses'


class Discourse(SpokenSource):
    """A discourse as a source."""

    type_label = 'discourse'

    class Meta:
        """Meta options for the Discourse model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Discourses'


class Lecture(SpokenSource):
    """A lecture as a source."""

    type_label = 'lecture'

    class Meta:
        """Meta options for the Lecture model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Lectures'


class Sermon(SpokenSource):
    """A sermon as a source."""

    type_label = 'sermon'

    class Meta:
        """Meta options for the Sermon model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Sermons'


class Statement(SpokenSource):
    """A statement as a source."""

    type_label = 'statement'

    class Meta:
        """Meta options for the Statement model."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        verbose_name_plural = 'Statements'
