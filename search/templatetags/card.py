from typing import Any

from django import template
from django.template import loader
from django.template.context import RequestContext
from django.utils.html import format_html
from django.utils.safestring import SafeString

from entities.models import Entity
# from django.apps import apps
from images.models import Image
from occurrences.models import Occurrence
from places.models import Place
from quotes.models import Quote
from search.templatetags.highlight import highlight
from sources.models import Source
from topics.models import Topic

register = template.Library()


@register.simple_tag(takes_context=True)
def card(context: RequestContext, obj: Any) -> SafeString:
    """Returns the card HTML for a supported ModularHistory object."""
    obj_name: str
    template_directory_name: str = ''

    # TODO: refactor
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

    greater_context = {**context.flatten(), **{'object': obj, obj_name: obj}}
    t = loader.get_template(f'{template_directory_name}/_card.html')
    response = t.render(greater_context)
    query = greater_context.get('query')
    return format_html(highlight(response, text=query)) if query else response
