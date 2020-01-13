from django import template
from django.apps import apps

# from sys import stderr

register = template.Library()


@register.filter()
def is_instance(value, arg: str):
    module, model = arg.split('.')
    cls = apps.all_models.get(module).get(model.lower())
    # print(f'{cls}: {isinstance(value, cls)}', file=stderr)
    return isinstance(value, cls)
