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
def detail(context: RequestContext, obj: Any):
    """TODO: add docstring."""
    obj_name: str
    template_directory_name: str = ''

    if isinstance(obj, Occurrence):
        obj_name = 'occurrence'
    elif isinstance(obj, Quote):
        obj_name = 'quote'
    elif isinstance(obj, Image):
        obj_name = 'image'
    elif isinstance(obj, Source):
        obj_name = 'source'
    elif isinstance(obj, Topic):
        obj_name = 'topic'
    elif isinstance(obj, Entity):
        obj_name = 'entity'
        template_directory_name = 'entities'
    else:
        raise ValueError(f'{type(obj)}: {obj}')

    # TODO
    template_directory_name = template_directory_name or f'{obj_name}s'

    greater_context = {**context.flatten(), **{
        obj_name: obj,
    }}

    template = loader.get_template(f'{template_directory_name}/_detail.html')
    response = template.render(greater_context)
    query = greater_context.get('query')
    return format_html(highlight(response, text=query)) if query else response
