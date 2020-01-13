from django import template
from django.urls import reverse

# from sys import stderr
from history.models import Model

register = template.Library()


@register.filter()
def get_detail_url(obj: Model) -> str:
    return reverse(f'{obj._meta.app_label}:detail', args=[obj.id])
