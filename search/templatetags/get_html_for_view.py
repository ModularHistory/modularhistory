from pprint import pprint
from typing import Dict, Optional, Union

import inflect
from django.template import Library, loader
from django.utils.html import SafeString, format_html

from modularhistory.models import SearchableModel
from search.templatetags.highlight import highlight

register = Library()


@register.filter(is_safe=True)
def get_html_for_view(
    model_instance: Union[Dict, SearchableModel],
    template_name: str,
    text_to_highlight: Optional[str] = None
) -> SafeString:
    """Return the HTML for the specified view of the model instance."""
    if '/' in template_name:
        model_name, template_name = template_name.split('/')
    elif isinstance(model_instance, SearchableModel):
        model_name = f'{model_instance.__class__.__name__}'.lower()
    else:
        raise ValueError(
            f'When rendering HTML for a serialized model instance, `template_name` '
            f'must include the model name; e.g., "image/card" rather than "card"'
        )
    app_name = inflect.engine().plural(model_name)
    template_directory_name = app_name
    template_name = f'{template_directory_name}/_{template_name}.html'
    template = loader.get_template(template_name)
    context = {
        model_name: model_instance,
        'object': model_instance,
        'show_edit_links': False,
    }
    response = template.render(context)
    if text_to_highlight:
        response = highlight(response, text_to_highlight=text_to_highlight)
    return format_html(response)
