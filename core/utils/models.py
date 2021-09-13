import logging
from datetime import datetime
from typing import Dict, Optional, Union

from django.apps import apps
from django.db.models import Model
from django.db.models.base import ModelBase
from django.template import loader
from django.utils import dateparse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.search.templatetags.highlight import highlight


def get_html_for_view(
    model_instance: Union[dict, Model],
    template_name: str,
    text_to_highlight: Optional[str] = None,
) -> SafeString:
    """Return the HTML for the specified view of the model instance."""
    if isinstance(model_instance, dict):
        app_name, model_name = model_instance['model'].split('.')
    else:
        model_cls: type[Model] = model_instance.__class__
        app_name = model_cls._meta.app_label
        model_name = model_cls.__name__.lower()
    template_directory_name = app_name
    template_name = f'{template_directory_name}/_{template_name}.html'
    logging.debug(f'Rendering {template_name} for {model_instance}...')
    template = loader.get_template(template_name)
    context = {
        model_name: model_instance,
        'object': model_instance,
    }
    response = template.render(context)
    if text_to_highlight:
        response = highlight(response, text_to_highlight=text_to_highlight)
    return format_html(response)


def serialize_model(model: Optional[ModelBase]) -> Optional[Dict[str, str]]:
    """
    Accepts a django.db.models.Model class and returns a serialized dict of
    it, so it may be sent to Celery workers over HTTP.
    """
    if model and isinstance(model, ModelBase):
        return {'app': model._meta.app_label, 'model': model._meta.model_name}
    return None


def deserialize_model(serialized_model: Optional[Dict[str, str]]) -> Optional[Model]:
    """
    Accepts a serialized django.db.models.Model class and returns the class.
    """
    if not serialized_model:
        return None
    app = serialized_model.get('app')
    model = serialized_model.get('model')
    if app and model:
        return apps.get_model(app, model)
    return None


def serialize_model_instance(instance: Optional[Model]) -> Optional[Dict[str, str]]:
    """
    Accept an django.db.models.Model instance and serializes it to a dictionary,
    so it may be serialized and sent to Celery workers over HTTP
    """
    if not instance:
        return None

    deserialized = serialize_model(instance.__class__)
    deserialized['id'] = str(instance.id)
    return deserialized


def deserialize_model_instance(
    serialized_instance: Optional[Dict[str, str]], *, select_for_update: bool = False
):
    """
    Accepts a serialized version of a Django model, and returns the instance.
    set kwargs select_for_update=True to lock the table row, preventing other
    threads from updating the instance while we work on it.
    """
    if not serialized_instance or not serialized_instance.get('id'):
        return None
    model = deserialize_model(serialized_instance)
    if not model:
        return None
    if select_for_update:
        return (
            model.objects.filter(id=serialized_instance.get('id')).select_for_update().first()
        )
    return model.objects.filter(id=serialized_instance.get('id')).first()


def has_been_indexed_since(instance: Model, *, timestamp: Optional[datetime]):
    """
    If instance has attribute indexed_at, we use this to determine if
    the instance has been indexed between the time the task was called
    was called, and now.

    If it has been, reindexing is unnecessary.
    """
    if not instance:
        return False
    if not getattr(instance, 'indexed_at', None):
        return False
    if not timestamp and not instance.indexed_at:
        return False
    if not timestamp and instance.indexed_at:
        return True
    if isinstance(timestamp, str):
        timestamp = dateparse.parse_datetime(timestamp)
    return instance.indexed_at > timestamp


def update_indexed_at(instance: Model, *, timestamp: Optional[datetime]):
    """
    Updates attribute indexed_at (if it exists) without triggering
    save_handler(). This prevents a loop from occuring
    """
    if not hasattr(instance, 'indexed_at'):
        return
    if not hasattr(instance.__class__, 'objects'):
        return
    instance.__class__.objects.filter(pk=instance.pk).update(indexed_at=timestamp)
