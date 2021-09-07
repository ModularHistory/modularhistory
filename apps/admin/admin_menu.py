"""Custom admin menu."""

from typing import Iterable

from admin_tools.menu import Menu, items
from django.apps import apps
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.admin.admin_site import admin_site

APPS_TO_INCLUDE = (
    'entities',
    'quotes',
    # 'occurrences',
    'propositions',
    'topics',
    'images',
    'places',
    'sources',
    'users',
    'flatpages',
    'redirects',
    'moderation',
)


def _get_models_registered_in_app(app: str) -> Iterable:
    _models = [
        model
        for model in apps.get_app_config(app).get_models()
        if model in admin_site.get_registry().keys()
    ]
    return _models


class AdminMenu(Menu):
    """Custom menu for ModularHistory's admin site."""

    class Media:
        """Static files to be included with the menu."""

        css = ()  # css = {'all': ('css/menu.css',)}
        js = ()  # js = ('js/menu.js',)

    def __init__(self, **kwargs):
        """Construct the admin menu."""
        super().__init__(**kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            *self._menu_items,
        ]

    @property
    def _menu_items(self) -> list[items.MenuItem]:
        menu_items = []
        for app in APPS_TO_INCLUDE:
            models = _get_models_registered_in_app(app)
            children = []
            for model_cls in models:
                model_name = model_cls.__name__
                children.append(
                    items.MenuItem(
                        model_name,
                        f'/{settings.ADMIN_URL_PREFIX}/{app}/{model_name.lower()}/',
                    )
                )
            menu_items.append(items.MenuItem(app, children=children))
        return menu_items
