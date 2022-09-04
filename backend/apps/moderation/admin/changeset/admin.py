from typing import TYPE_CHECKING

from django.contrib import admin

from apps.admin.admin_site import admin_site
from apps.admin.inlines import StackedInline
from apps.moderation.models import Change, ChangeSet

if TYPE_CHECKING:
    from django.http.request import HttpRequest


class ChangesInline(StackedInline):
    """Inline admin for changes that comprise a change set."""

    model = Change
    fk_name = 'set'
    extra = 0


class ChangeSetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    fieldsets = (('Moderation', {'fields': ('description',)}),)
    inlines = [ChangesInline]
    list_display = ('created_date', 'moderation_status')
    list_filter = ('moderation_status',)

    def get_actions(self, request: 'HttpRequest'):
        """Return the batch actions available to the admin list view."""
        actions = super().get_actions(request)
        # Remove the delete_selected action if it exists.
        try:
            del actions['delete_selected']
        except KeyError:
            pass
        return actions

    def has_add_permission(self, request: 'HttpRequest', obj=None):
        """Return a boolean reflecting whether to include the "Add" button in the admin."""
        # Always return False; changesets should not be created manually.
        return False


admin_site.register(ChangeSet, ChangeSetAdmin)
