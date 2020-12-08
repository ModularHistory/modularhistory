"""Model classes for web pages."""

from modularhistory.fields import ExtraField

from .textual_source import TextualSource

JSON_FIELD_NAME = 'extra'


# TODO: Creat WebSite model


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

    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            self.attributee_html,
            f'"{self.linked_title}"',
            f'<i>{self.website_title}</i>',
            self.organization_name,
            self.date.string if self.date else '',
            f'retrieved from <a target="_blank" href="{self.url}">{self.url}</a>',
        ]
        return self.components_to_html(components)
