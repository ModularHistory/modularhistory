from django import template

register = template.Library()


@register.inclusion_tag('sources/_pdf_viewer.html')
def render_pdf_viewer(source):
    """TODO: add docstring."""
    return {'source': source}
