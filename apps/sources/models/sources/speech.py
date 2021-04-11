"""Model classes for spoken sources."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.places.models import Venue
from apps.sources.models.source import PolymorphicSource

SPEECH_TYPES = (
    ('speech', 'Speech'),
    ('address', 'Address'),
    ('discourse', 'Discourse'),
    ('lecture', 'Lecture'),
    ('sermon', 'Sermon'),
    ('statement', 'Statement'),
)


class Speech(PolymorphicSource):
    """Spoken words (e.g., a speech, lecture, or discourse)."""

    type = models.CharField(
        verbose_name=_('speech type'),
        max_length=10,
        choices=SPEECH_TYPES,
        default=SPEECH_TYPES[0][0],
    )

    audience = models.CharField(max_length=100, null=True, blank=True)

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        type_label = self.type
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
