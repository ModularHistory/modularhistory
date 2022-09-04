from admin_auto_filters.views import AutocompleteJsonView as _AutocompleteJsonView
from django.contrib.admin import ModelAdmin


class AutocompleteJsonView(_AutocompleteJsonView):
    """Used by autocomplete widgets in admin."""

    model_admin = ModelAdmin

    def get_paginator(self, *args, **kwargs):
        return self.paginator_class(*args, **kwargs)
