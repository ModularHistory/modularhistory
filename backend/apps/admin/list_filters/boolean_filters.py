"""AutocompleteFilter based on https://github.com/farhan0581/django-admin-autocomplete-filter."""

from django.contrib.admin import SimpleListFilter

from core.constants.strings import NO, YES


class BooleanListFilter(SimpleListFilter):
    """Filters based on a boolean (yes or no) field or property."""

    def lookups(self, request, model_admin):
        """Return an iterable of tuples (value, verbose value) containing filter input options."""
        return (YES, YES), (NO, NO)


class HasValueFilter(BooleanListFilter):
    """Filters based on whether model instances have a value for the specified field."""

    field: str

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        option = self.value()
        if option in (YES, NO):
            return queryset.filter(**{f'{self.field}__isnull': option != YES})
        return queryset


class HasRelationFilter(BooleanListFilter):
    """Filters based on whether model instances have the specified relation."""

    relation: str

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        option = self.value()
        if option == YES:
            return queryset.exclude(**{self.relation: None})
        elif option == NO:
            return queryset.filter(**{self.relation: None})
        return queryset
