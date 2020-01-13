from django import template

register = template.Library()


@register.inclusion_tag('occurrences/_row.html')
def occurrence_row(occurrence):
    # TODO: Do math to determine columns
    return {'occurrence': occurrence}
