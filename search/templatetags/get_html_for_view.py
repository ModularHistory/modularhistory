import logging
from typing import Dict, Optional, Union

import inflect
from django.template import Library, loader
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.models import Model
from search.templatetags.highlight import highlight

register = Library()


@register.filter(is_safe=True)
def get_html_for_view(
    model_instance: Union[Dict, Model],
    view_name: str,
    text_to_highlight: Optional[str] = None,
) -> SafeString:
    """Return the HTML for the specified view of the model instance."""
    if isinstance(model_instance, dict):
        try:
            app_name, model_name = model_instance['model'].split('.')
        except KeyError as e:
            raise KeyError(f'{e} was not found in {model_instance}')
    elif isinstance(model_instance, Model):
        model_name = f'{model_instance.__class__.__name__}'.lower()
        app_name = model_instance.__class__.get_meta().app_label
    else:
        raise ValueError(
            'When rendering HTML for a serialized model instance, `template_name` '
            'must include the model name; e.g., "image/card" rather than "card"'
        )
    template_directory_name = app_name
    template_name = f'{template_directory_name}/_{view_name}.html'
    context = {
        model_name: model_instance,
        'object': model_instance,
    }
    logging.info(f'Rendering {template_name} for {model_instance}...')
    template = loader.get_template(template_name)
    try:
        response = template.render(context)
    except ValueError:
        template_directory_name = inflect.engine().plural(model_name)
        template_name = f'{template_directory_name}/_{view_name}.html'
        logging.info(f'Rendering {template_name} for {model_instance}...')
        template = loader.get_template(template_name)
        response = template.render(context)
    if text_to_highlight:
        response = highlight(response, text_to_highlight=text_to_highlight)
    return format_html(response)
