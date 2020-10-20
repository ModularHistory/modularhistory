"""Model classes for web pages."""

from modularhistory.utils.html import soupify

from modularhistory.fields import ExtraField
from sources.models.textual_source import TextualSource

JSON_FIELD_NAME = 'extra'


class WebPage(TextualSource):
    """A web page (as a source)."""

    # TODO: Creat WebSite model

    # website_title = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    website_title = ExtraField(json_field_name=JSON_FIELD_NAME)

    # organization_name = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    organization_name = ExtraField(json_field_name=JSON_FIELD_NAME)

    def __str__(self) -> str:
        """TODO: write docstring."""
        return soupify(self.__html__).get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            self.attributee_string,
            self.linked_title,
            f'<i>{self.website_title}</i>',
            self.organization_name,
            self.date.string if self.date else '',
            f'retrieved from <a target="_blank" href="{self.url}">{self.url}</a>'
        ]
        return self.components_to_html(components)
