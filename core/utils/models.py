import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

from django.template import loader
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.search.templatetags.highlight import highlight

if TYPE_CHECKING:
    from core.models.model import Model


def get_html_for_view(
    model_instance: Union[Dict, 'Model'],
    template_name: str,
    text_to_highlight: Optional[str] = None,
) -> SafeString:
    """Return the HTML for the specified view of the model instance."""
    if isinstance(model_instance, dict):
        app_name, model_name = model_instance['model'].split('.')
    else:
        app_name = model_instance.__class__.get_meta().app_label
        model_name = model_instance.__class__.__name__.lower()
    template_directory_name = app_name
    template_name = f'{template_directory_name}/_{template_name}.html'
    logging.debug(f'Rendering {template_name} for {model_instance}...')
    template = loader.get_template(template_name)
    context = {
        model_name: model_instance,
        'object': model_instance,
    }
    response = template.render(context)
    if text_to_highlight:
        response = highlight(response, text_to_highlight=text_to_highlight)
    return format_html(response)
