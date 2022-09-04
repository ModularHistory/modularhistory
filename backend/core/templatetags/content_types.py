import logging
from typing import Optional, Union

from django import template
from django.apps import apps
from django.utils.module_loading import import_string

from core.constants.content_types import MODEL_CLASS_PATHS
from core.models.model import ExtendedModel

register = template.Library()


@register.filter()
def class_name(instance) -> str:
    """Return the instance's class name."""
    return instance.__class__.__name__


@register.filter()
def is_instance(instance: Union[dict, ExtendedModel], arg: str) -> bool:
    """
    Determine whether model_instance is an instance of the specified model class.

    `arg` should be in the form 'module_name.ModelName'.
    """
    if isinstance(instance, dict):
        return instance.get('model') == arg.lower()
    module_name, model_name = arg.split('.')
    model_instance = instance
    model_name = model_name.lower()
    model_cls_path: Optional[str] = MODEL_CLASS_PATHS.get(model_name)
    if model_cls_path:
        model_class = import_string(model_cls_path)
        return isinstance(model_instance, model_class)
    else:
        module = apps.all_models.get(module_name)
        if module:
            model_class = module.get(model_name)
            return isinstance(model_instance, model_class)
        logging.error(f'Unable to locate {module_name}')
    return False
