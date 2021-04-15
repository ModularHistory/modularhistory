"""AutocompleteFilter based on https://github.com/farhan0581/django-admin-autocomplete-filter."""

from django.contrib.admin import SimpleListFilter

from core.constants.strings import NO, YES


class BooleanListFilter(SimpleListFilter):
    """Filters based on a boolean (yes or no) field/property."""

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value) containing filter input options."""
        return (YES, YES), (NO, NO)
