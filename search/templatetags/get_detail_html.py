from typing import Dict, Optional, Union

from django.template import Library
from django.utils.safestring import SafeString

from modularhistory.models import Model
from modularhistory.utils.models import get_html_for_view

register = Library()


@register.filter(is_safe=True)
def get_detail_html(
    model_instance: Union[Dict, Model],
    text_to_highlight: Optional[str] = None,
) -> SafeString:
    """Return the HTML for the detail view of the model instance."""
    return get_html_for_view(
        model_instance, 'detail', text_to_highlight=text_to_highlight
    )
