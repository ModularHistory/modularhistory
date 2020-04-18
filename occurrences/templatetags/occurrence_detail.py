from django import template
from occurrences.models import Occurrence

register = template.Library()


@register.inclusion_tag('occurrences/_detail.html')
def occurrence_detail(occurrence: Occurrence):
    # TODO: Do math to determine columns
    return occurrence.get_context()
