from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('places/_card.html', takes_context=True)
def place_card(context: RequestContext, place):
    return {**context.flatten(), **{
        'place': place,
    }}
