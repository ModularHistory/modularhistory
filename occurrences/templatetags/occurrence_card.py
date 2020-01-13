from django import template
from django.template.context import RequestContext

register = template.Library()


@register.inclusion_tag('occurrences/_card.html', takes_context=True)
def occurrence_card(context: RequestContext, occurrence):
    return {**context.flatten(), **{
        'occurrence': occurrence,
    }}
