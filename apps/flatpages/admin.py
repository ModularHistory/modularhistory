
from apps.admin.admin_site import admin_site
from apps.admin.model_admin import FORM_FIELD_OVERRIDES
from apps.flatpages.models import FlatPage
from apps.moderation.admin.moderated_model import ModeratedModelAdmin


class FlatPageAdmin(ModeratedModelAdmin):
    """Admin for flat pages."""

    formfield_overrides = FORM_FIELD_OVERRIDES
    list_display = ('url', 'title')
    list_filter = ('sites', 'registration_required')
    search_fields = ('url', 'title')


admin_site.register(FlatPage, FlatPageAdmin)