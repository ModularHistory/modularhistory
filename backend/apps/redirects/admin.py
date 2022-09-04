from django.contrib import admin

from apps.admin.admin_site import admin_site
from apps.redirects.models import Redirect


class RedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path')
    list_filter = ('site',)
    search_fields = ('old_path', 'new_path')
    radio_fields = {'site': admin.VERTICAL}


admin_site.register(Redirect, RedirectAdmin)
