from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('entities/_card.html', takes_context=True)
def entity_card(context: RequestContext, entity):
    return {**context.flatten(), **{
        'entity': entity,
    }}
