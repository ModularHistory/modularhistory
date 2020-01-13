from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('quotes/_card.html', takes_context=True)
def quote_card(context: RequestContext, quote):
    return {**context.flatten(), **{
        'quote': quote,
    }}
