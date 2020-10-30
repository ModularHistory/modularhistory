from django import template
from django.utils.safestring import SafeString

from modularhistory.models import SearchableModel

register = template.Library()


@register.filter(is_safe=True)
def get_html_for_view(model_instance: SearchableModel, view: str) -> SafeString:
    """Return the HTML for the specified view of the model instance."""
    return model_instance.get_html_for_view(view)
