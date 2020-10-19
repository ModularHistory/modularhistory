from typing import Any

from django.template import Library, loader
from django.template.context import RequestContext
from django.utils.html import format_html

from entities.models import Entity
# from django.apps import apps
from images.models import Image
from occurrences.models import Occurrence
from quotes.models import Quote
from search.templatetags.highlight import highlight
from sources.models import Source
from topics.models import Topic

register = Library()


@register.simple_tag(takes_context=True)
def detail(context: RequestContext, model_instance: Any):
    """TODO: add docstring."""
    obj_name: str
    template_directory_name: str = ''

    if isinstance(model_instance, Occurrence):
        obj_name = 'occurrence'
    elif isinstance(model_instance, Quote):
        obj_name = 'quote'
    elif isinstance(model_instance, Image):
        obj_name = 'image'
    elif isinstance(model_instance, Source):
        obj_name = 'source'
    elif isinstance(model_instance, Topic):
        obj_name = 'topic'
    elif isinstance(model_instance, Entity):
        obj_name = 'entity'
        template_directory_name = 'entities'
    else:
        raise ValueError(f'{type(model_instance)}: {model_instance}')

    # TODO
    template_directory_name = template_directory_name or f'{obj_name}s'

    greater_context = {**context.flatten(), **{
        obj_name: model_instance,
    }}

    template = loader.get_template(f'{template_directory_name}/_detail.html')
    response = template.render(greater_context)
    query = greater_context.get('query')
    return format_html(highlight(response, text_to_highlight=query)) if query else response
