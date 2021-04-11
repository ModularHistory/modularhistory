"""Model classes for web pages."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.mixins.textual_source import TextualSourceMixin
from apps.sources.models.publication import AbstractPublication
from apps.sources.models.source import PolymorphicSource
from modularhistory.fields import ExtraField

from .textual_source import TextualSource

JSON_FIELD_NAME = 'extra'


class Website2(AbstractPublication):
    """A website."""

    owner = models.CharField(
        verbose_name=_('owner'), max_length=100, null=True, blank=True
    )


class PolymorphicWebPage(PolymorphicSource, TextualSourceMixin):
    """A web page."""

    website = models.ForeignKey(
        'sources.Website2', null=True, blank=True, on_delete=models.CASCADE
    )


class WebPage(TextualSource):
    """A web page (as a source)."""

    website_title = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )
    organization_name = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )

    class FieldNames(TextualSource.FieldNames):
        website = 'publication'

    inapplicable_fields = [
        FieldNames.collection,
    ]
    searchable_fields = [FieldNames.string, f'{FieldNames.website}__name']

    def clean(self):
        """Prepare the article to be saved."""
        super().clean()
        if self.publication:
            if self.publication.type != 'sources.website':
                raise ValidationError('Web page publisher must be a website.')
        else:
            raise ValidationError('Web page must have an associated website.')

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        components = [
            self.attributee_html,
            f'"{self.linked_title}"',
            f'<i>{self.website_title}</i>',
            self.organization_name,
            self.date.string if self.date else '',
            f'retrieved from <a target="_blank" href="{self.url}">{self.url}</a>',
        ]
        return self.components_to_html(components)
