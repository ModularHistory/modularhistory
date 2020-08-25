from django import forms
from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from tinymce.widgets import TinyMCE

from admin import admin_site
from .models import StaticPage


class StaticPageForm(FlatpageForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Media:
        js = ('scripts/mce.js',)


class StaticPageAdmin(FlatPageAdmin):
    form = StaticPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (('Advanced options',), {
            'classes': ('collapse', ),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )


# admin.site.unregister(FlatPage)
admin_site.register(StaticPage, StaticPageAdmin)
