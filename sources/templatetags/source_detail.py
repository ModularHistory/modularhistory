from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('sources/_detail.html', takes_context=True)
def source_detail(context: RequestContext, quote):
    return {**context.flatten(), **{
        'source': source,
    }}
