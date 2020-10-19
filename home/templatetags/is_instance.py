"""Template filter for checking model object types."""

from django import template
from django.apps import apps
from django.utils.module_loading import import_string

from modularhistory.constants import MODEL_CLASS_PATHS

register = template.Library()


@register.filter()
def is_instance(model_instance, arg: str) -> bool:
    """
    Determine whether model_instance is an instance of the specified model class.

    `arg` should be in the form 'module_name.ModelName'.
    """
    module_name, model_name = arg.split('.')
    model_name = model_name.lower()
    model_cls_path: str = MODEL_CLASS_PATHS.get(model_name)
    if model_cls_path:
        model_class = import_string(model_cls_path)
    else:
        model_class = apps.all_models.get(module_name).get(model_name)
    return isinstance(model_instance, model_class)
