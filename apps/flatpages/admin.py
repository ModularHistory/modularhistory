from apps.admin.admin_site import admin_site
from apps.flatpages.models import FlatPage
from apps.moderation.admin.moderated_model import ModeratedModelAdmin


class FlatPageAdmin(ModeratedModelAdmin):
    """Admin for flat pages."""

    model = FlatPage

    list_display = ('path', 'title')
    list_filter = ModeratedModelAdmin.list_filter + ['sites', 'registration_required']
    search_fields = ('path', 'title')


admin_site.register(FlatPage, FlatPageAdmin)
