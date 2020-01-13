from django import template
from django.template.context import RequestContext
register = template.Library()


@register.inclusion_tag('images/_detail.html', takes_context=True)
def image_detail(context: RequestContext, image):
    return {**context.flatten(), **{
        'image': image,
    }}
