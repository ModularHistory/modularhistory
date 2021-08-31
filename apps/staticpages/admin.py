from django.contrib.flatpages.admin import FlatPageAdmin as BaseFlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from apps.admin.model_admin import admin_site
from core.fields.html_field import TrumbowygWidget


class FlatPageAdmin(BaseFlatPageAdmin):
    """Admin for static pages."""

    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (
            ('Advanced options',),
            {
                'classes': ('collapse',),
                'fields': (
                    'enable_comments',
                    'registration_required',
                    'template_name',
                ),
            },
        ),
    )


admin_site.register(FlatPage, FlatPageAdmin)
