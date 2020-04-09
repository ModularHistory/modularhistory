from django import template

register = template.Library()


@register.inclusion_tag('occurrences/_detail.html')
def occurrence_detail(occurrence):
    # TODO: Do math to determine columns
    return {
        'occurrence': occurrence,
    }
