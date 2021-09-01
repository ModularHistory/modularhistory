from django.utils.translation import gettext_lazy as _

from apps.admin.admin_site import admin_site
from apps.flatpages.forms import FlatPageForm
from apps.flatpages.models import FlatPage
from apps.moderation.admin.moderated_model import ModeratedModelAdmin


class FlatPageAdmin(ModeratedModelAdmin):
    form = FlatPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (
            _('Advanced options'),
            {
                'classes': ('collapse',),
                'fields': ('registration_required', 'template_name'),
            },
        ),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'registration_required')
    search_fields = ('url', 'title')


admin_site.register(FlatPage, FlatPageAdmin)
