from django import template

from modularhistory.models import Model

register = template.Library()


@register.filter()
def get_admin_url(model_instance: Model) -> str:
    """Returns the URL of the model instance's admin page."""
    if not isinstance(model_instance, Model):
        raise ValueError(
            f'{model_instance} (of type "{type(model_instance)}") is not a model instance.'
        )
    return model_instance.get_admin_url()
