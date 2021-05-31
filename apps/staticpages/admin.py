from django import forms
from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from django.contrib.flatpages.models import FlatPage

from apps.admin.model_admin import admin_site
from apps.staticpages.models import StaticPage
from core.fields.html_field import TrumbowygWidget


class StaticPageForm(FlatpageForm):
    """Form for adding/editing static pages."""

    content = forms.CharField(widget=TrumbowygWidget())  # noqa: WPS110

    class Meta:
        model = StaticPage
        fields = '__all__'


class StaticPageAdmin(FlatPageAdmin):
    """Admin for static pages."""

    form = StaticPageForm
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


admin_site.register(StaticPage, StaticPageAdmin)
admin_site.register(FlatPage, FlatPageAdmin)
