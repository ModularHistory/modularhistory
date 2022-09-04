from django.db.models import Q
from django.db.models.query import QuerySet

from apps.admin.views import AutocompleteJsonView
from apps.users.models import User


class UserSearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self) -> 'QuerySet[User]':
        """Return the filtered queryset."""
        if self.term:
            return User.objects.filter(
                Q(first_name__icontains=self.term)
                | Q(last_name__icontains=self.term)
                | Q(handle__icontains=self.term)
            )
        return User.objects.all()
