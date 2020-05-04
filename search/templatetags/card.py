from typing import Any

from django import template
from django.template import loader
from django.template.context import RequestContext
from django.utils.safestring import mark_safe
from haystack.utils.highlighting import Highlighter

from entities.models import Entity
# from django.apps import apps
from images.models import Image
from occurrences.models import Occurrence
from places.models import Place
from quotes.models import Quote
from sources.models import Source
from topics.models import Topic

register = template.Library()


@register.simple_tag(takes_context=True)
def card(context: RequestContext, obj: Any):
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
    elif isinstance(obj, Place):
        obj_name = 'place'
    elif isinstance(obj, Entity):
        obj_name = 'entity'
        template_directory_name = 'entities'
    else:
        raise ValueError(f'{type(obj)}: {obj}')

    # TODO
    template_directory_name = template_directory_name or f'{obj_name}s'

    context = {**context.flatten(), **{
        obj_name: obj,
    }}

    t = loader.get_template(f'{template_directory_name}/_card.html')
    response = t.render(context)

    query = context.get('query')
    if query:
        highlighter = Highlighter(query)
        return mark_safe(highlighter.highlight(response))

    return response
