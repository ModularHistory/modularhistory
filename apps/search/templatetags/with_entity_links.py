import logging
import re

from django import template
from django.urls import reverse
from django.utils.html import format_html

from core.fields.html_field import ENTITY_NAME_REGEX

register = template.Library()


@register.filter(is_safe=True)
def with_entity_links(html: str):
    """Return the HTML string with entity names linked to detail pages."""
    try:
        if re.search(ENTITY_NAME_REGEX, html):
            processed_entity_keys = []
            for match in re.finditer(ENTITY_NAME_REGEX, html):
                key = match.group(1).strip()
                entity_name = match.group(2)
                # Process the entity name if it hasn't already been processed
                if key not in processed_entity_keys:
                    processed_entity_keys.append(key)
                    try:
                        entity_link = (
                            f'<a href="{reverse("entities:detail", args=[key])}" '
                            f'target="_blank">{entity_name}</a>'
                        )
                        html = html.replace(match.group(0), entity_link, 1)
                    except Exception as error:
                        logging.error(f'{error}')
        return format_html(html)
    except TypeError as err:
        logging.error(
            f'`with_entity_links` received value of type {type(html)} {html}; {err}'
        )
        return html
