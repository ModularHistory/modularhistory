from typing import Type

from apps.admin.inlines import TabularInline


class AbstractSourcesInline(TabularInline):
    """Inline admin for sources."""

    model: Type

    autocomplete_fields = ['source']
    # TODO: fix JSON widget so pages can be included in the inline editor
    exclude = ['cache', 'pages', 'citation_html', 'verified']
    readonly_fields = ['escaped_citation_html', 'pk']
    verbose_name = 'citation'
    verbose_name_plural = 'sources'

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'

    def get_fields(self, request, model_instance) -> list[str]:
        fields = list(super().get_fields(request, model_instance))
        ordered_fields = ['citation_phrase']
        for field in ordered_fields:
            if field in fields:
                fields.remove(field)
                fields.insert(0, field)
        return fields

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('source')
