from django.db.models.base import Model

from apps.admin.inlines import TabularInline


class AbstractRelatedQuotesInline(TabularInline):
    """Abstract base inline for related quotes."""

    model: Model

    autocomplete_fields: list[str] = ['quote']
    extra = 0

    # https://django-grappelli.readthedocs.io/en/latest/customization.html#inline-sortables
    sortable_field_name = 'position'
