"""Model classes for web pages."""

from bs4 import BeautifulSoup

from modularhistory.fields import ExtraField
from sources.models.textual_source import TextualSource


class WebPage(TextualSource):
    """A web page (as a source)."""

    # TODO: Creat WebSite model

    # website_title = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    website_title = ExtraField(json_field_name='extra')

    # organization_name = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    organization_name = ExtraField(json_field_name='extra')

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

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
