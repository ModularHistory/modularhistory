from typing import Any

import inflect
from django.template import Library, loader
from django.template.context import RequestContext
from django.utils.html import format_html

# from django.apps import apps
from search.templatetags.highlight import highlight

register = Library()

ALLOWED_MODELS = (
    'occurrence',
    'quote',
    'image',
    'source',
    'topic',
    'place',
    'entity',
)


@register.simple_tag(takes_context=True)
def detail(context: RequestContext, model_instance: Any):
    """TODO: add docstring."""
    model_name = f'{model_instance.__class__.__name__}'.lower()
    if model_name not in ALLOWED_MODELS:
        raise ValueError(f'{type(model_instance)}: {model_instance}')
    template_directory_name = inflect.engine().plural(model_name)
    greater_context = {
        **context.flatten(),
        **{model_name: model_instance},
    }
    template = loader.get_template(f'{template_directory_name}/_detail.html')
    response = template.render(greater_context)
    query = greater_context.get('query')
    return (
        format_html(highlight(response, text_to_highlight=query)) if query else response
    )
