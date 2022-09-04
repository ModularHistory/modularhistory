import logging
from typing import Optional, Union

import inflect
from django.template import Library, loader
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.search.templatetags.highlight import highlight
from core.models.model import ExtendedModel

register = Library()


@register.filter(is_safe=True)
def get_html_for_view(
    model_instance: Union[dict, ExtendedModel],
    view_name: str,
    text_to_highlight: Optional[str] = None,
) -> SafeString:
    """Return the HTML for the specified view of the model instance."""
    if isinstance(model_instance, dict):
        try:
            app_name, model_name = model_instance['model'].split('.')
        except KeyError as e:
            raise KeyError(f'{e} was not found in {model_instance}')
    elif isinstance(model_instance, ExtendedModel):
        model_name = f'{model_instance.__class__.__name__}'.lower()
        app_name = model_instance.__class__._meta.app_label
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
    logging.debug(f'Rendering {template_name} for {model_instance}...')
    template = loader.get_template(template_name)
    try:
        response = template.render(context)
    except Exception as err:
        logging.error(f'ERROR: {type(err)}: {err}')
        template_directory_name = inflect.engine().plural(model_name)
        template_name = f'{template_directory_name}/_{view_name}.html'
        logging.debug(f'Rendering {template_name} for {model_instance}...')
        template = loader.get_template(template_name)
        response = template.render(context)
    if text_to_highlight:
        response = highlight(response, text_to_highlight=text_to_highlight)
    return format_html(response)
