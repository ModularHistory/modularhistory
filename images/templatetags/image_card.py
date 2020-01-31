from django import template
from django.template.context import RequestContext
register = template.Library()


@register.inclusion_tag('images/_card.html', takes_context=True)
def image_card(context: RequestContext, image):
    return {**context.flatten(), **{
        'image': image,
        'object': image,  # TODO
    }}
