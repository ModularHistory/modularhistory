from django import template
from django.template.context import RequestContext

from occurrences.models import Occurrence

register = template.Library()


@register.inclusion_tag('occurrences/_detail.html', takes_context=True)
def occurrence_detail(context: RequestContext, occurrence: Occurrence):
    # TODO: Do math to determine columns
    return {**context.flatten(), **occurrence.get_context()}
