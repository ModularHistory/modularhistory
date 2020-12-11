from typing import Dict, Union

from django import template
from django.apps import apps
from django.utils.module_loading import import_string

from modularhistory.constants.misc import MODEL_CLASS_PATHS
from modularhistory.models import Model

register = template.Library()


@register.filter()
def class_name(instance) -> str:
    """Return the instance's class name."""
    return instance.__class__.__name__


@register.filter()
def is_instance(instance: Union[Dict, Model], arg: str) -> bool:
    """
    Determine whether model_instance is an instance of the specified model class.

    `arg` should be in the form 'module_name.ModelName'.
    """
    if isinstance(instance, dict):
        return instance.get('model') == arg.lower()
    module_name, model_name = arg.split('.')
    model_instance = instance
    model_name = model_name.lower()
    model_cls_path: str = MODEL_CLASS_PATHS.get(model_name)
    if model_cls_path:
        model_class = import_string(model_cls_path)
    else:
        model_class = apps.all_models.get(module_name).get(model_name)
    return isinstance(model_instance, model_class)
