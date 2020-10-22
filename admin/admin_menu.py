"""
ModularHistory's custom admin menu.

This custom admin menu is activated by the following line in settings.py:
    ADMIN_TOOLS_MENU = 'modularhistory.admin_menu.AdminMenu'
"""

from typing import Iterable

from admin_tools.menu import Menu, items
from django.apps import apps
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from admin.admin_site import admin_site

APPS_TO_INCLUDE = (
    'entities',
    'quotes',
    'occurrences',
    'sources',
    'images',
    'topics',
    'places',
    'staticpages',
    'account'
)


def _get_models_registered_in_app(app: str) -> Iterable:
    app_models = apps.get_app_config(app).get_models()
    return [model for model in app_models if model in admin_site.get_registry().keys()]


class AdminMenu(Menu):
    """Custom menu for ModularHistory's admin site."""

    apps_to_include = APPS_TO_INCLUDE

    class Media:
        """Static files to be included with the menu."""
        css = ()  # css = {'all': ('css/menu.css',)}
        js = ()  # js = ('js/menu.js',)

    @property
    def menu_items(self):
        menu_items = []
        for app in self.apps_to_include:
            models = _get_models_registered_in_app(app)
            children = []
            for model_cls in models:
                model_name = model_cls.__name__
                children.append(items.MenuItem(model_name, f'/admin/{app}/{model_name.lower()}/'))
            menu_items.append(items.MenuItem(app, children=children))
        return menu_items

    def __init__(self, **kwargs):
        """Constructs the admin menu."""
        super().__init__(**kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            items.AppList(
                title='Applications',
                exclude=[
                    'django.contrib.*',
                    'social_django.*',
                    'django_celery_*'
                ]
            ),
        ] + self.menu_items
        # self.children += [
        #     items.MenuItem('Entities', children=self.entity_menu_items),
        #     items.MenuItem('Quotes', '/admin/quotes/quote/'),
        #     items.MenuItem('Occurrences', children=[
        #         items.MenuItem('Occurrences', '/admin/occurrences/occurrence/'),
        #         items.MenuItem('Occurrence chains', '/admin/occurrences/occurrencechain/'),
        #     ]),
        #     items.MenuItem('Sources', children=[
        #         items.MenuItem('Sources', '/admin/sources/source/'),
        #         items.MenuItem('Citations', '/admin/sources/citation/'),
        #         items.MenuItem('Collections', '/admin/sources/collection/'),
        #         items.MenuItem('Files', '/admin/sources/sourcefile/'),
        #         items.MenuItem('Repositories', '/admin/sources/repository/'),
        #     ]),
        #     items.MenuItem('Images', children=[
        #         items.MenuItem('Images', '/admin/images/image/'),
        #         items.MenuItem('Videos', '/admin/images/video/'),
        #     ]),
        #     items.MenuItem('Topics', '/admin/topics/topic/'),
        #     items.MenuItem('Places', '/admin/places/place/'),
        #     items.MenuItem('Pages', '/admin/staticpages/staticpage/'),
        #     items.MenuItem('Tasks', children=[
        #         items.MenuItem('Periodic tasks', '/admin/django_celery_beat/periodictask/'),
        #         items.MenuItem('Task results', '/admin/django_celery_results/taskresult/'),
        #     ]),
        #     items.MenuItem('Users', children=[
        #         items.MenuItem('Users', '/admin/account/user/'),
        #         items.MenuItem('Associations', '/admin/social_django/association/'),
        #         items.MenuItem('Nonces', '/admin/social_django/nonce/'),
        #         items.MenuItem('Social Auths', '/admin/social_django/usersocialauth/'),
        #     ])
        # ]

    # def init_with_context(self, context):
    #     """Use this method if you need to access the request context."""
    #     super().init_with_context(context)
    #     # Use sessions to store the visited pages stack
    #     # history = request.session.get('modularhistory', [])
    #     # for item in history:
    #     #     self.children.append(MenuItem(
    #     #         title=item['title'],
    #     #         url=item['url']
    #     #     ))
    #     # # Add the current page to the history
    #     # history.insert(0, {
    #     #     'title': context['title'],
    #     #     'url': request.META['PATH_INFO']
    #     # })
    #     # if len(history) > 10:
    #     #     history = history[:10]
    #     # request.session['modularhistory'] = history
