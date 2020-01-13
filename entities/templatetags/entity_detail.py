from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('entities/_detail.html', takes_context=True)
def entity_detail(context: RequestContext, entity):
    return {**context.flatten(), **{
        'entity': entity,
    }}
