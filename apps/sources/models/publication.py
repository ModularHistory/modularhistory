from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.moderation.models import ModeratedModel
from core.fields.html_field import HTMLField
from core.models.typed import TypedModel, TypedModelManager
from core.utils.html import soupify

PUBLICATION_TYPES = (
    ('journal', 'Journal'),
    ('newspaper', 'Newspaper'),
    ('magazine', 'Magazine'),
)


class AbstractPublication(ModeratedModel):
    """Abstract base class for publications."""

    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        blank=True,
        unique=True,
    )
    aliases = models.CharField(
        verbose_name=_('aliases'),
        max_length=100,
        blank=True,
    )
    description = HTMLField(
        verbose_name=_('description'),
        blank=True,
        paragraphed=True,
    )

    class Meta:
        abstract = True


class Publication(TypedModel, AbstractPublication):
    """A publication, such as a newspaper, magazine, or journal."""

    class Meta:
        ordering = ['name']

    objects = TypedModelManager()
    searchable_fields = ['name', 'aliases']

    def __str__(self) -> str:
        """Return the publication's string representation."""
        return soupify(self.html).get_text()

    def save(self, *args, **kwargs):
        AbstractPublication.save(self, *args, **kwargs)

    def clean(self):
        """Prepare the publication to be saved."""
        super().clean()
        if self.type == 'sources.publication' or not self.type:
            raise ValidationError('Publication must have a type.')
        else:
            # Prevent a RuntimeError when saving a new publication
            self.recast(self.type)

    @property
    def html(self) -> SafeString:
        """Return the publication's HTML representation."""
        return format_html(self.__html__())

    def __html__(self) -> str:
        """Return the publication's HTML representation."""
        return f'<i>{self.name}</i>'


class Journal(Publication):
    """A journal that publishes articles."""


class Magazine(Publication):
    """A magazine that publishes articles."""


class Newspaper(Publication):
    """A newspaper that publishes articles."""
