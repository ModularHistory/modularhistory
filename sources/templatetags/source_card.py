from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('sources/_card.html', takes_context=True)
def source_card(context: RequestContext, source):
    return {**context.flatten(), **{
        'source': source,
    }}
