from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('topics/_card.html', takes_context=True)
def topic_card(context: RequestContext, topic):
    return {**context.flatten(), **{
        'topic': topic,
    }}
