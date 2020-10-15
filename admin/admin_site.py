from django.contrib.admin import AdminSite as BaseAdminSite
from massadmin.massadmin import mass_change_selected


class AdminSite(BaseAdminSite):
    """TODO: add docstring."""

    site_header = 'ModularHistory administration'


admin_site = AdminSite(name='admin')
admin_site.add_action(mass_change_selected)
