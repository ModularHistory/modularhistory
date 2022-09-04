from django.contrib.admin import AdminSite as BaseAdminSite


class AdminSite(BaseAdminSite):
    """ModularHistory's admin site."""

    site_header = 'ModularHistory administration'

    def get_registry(self):
        """Return a dict of Model -> ModelAdmin."""
        return self._registry


admin_site = AdminSite(name='admin')
