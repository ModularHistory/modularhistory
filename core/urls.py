"""
ModularHistory URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/

Examples:
    Function views:
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    Class-based views:
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    Including another URL config:
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from graphene_django.views import GraphQLView
from watchman.views import bare_status

from apps.admin.model_admin import admin_site
from apps.users.api.views import set_csrf_token
from core import errors
from core.environment import IS_DEV
from core.sitemap import sitemaps

if TYPE_CHECKING:
    from django.http import HttpRequest


class ModelGraphView(TemplateView):
    """View for ModularHistory's model graph."""

    template_name = 'model_graph.html'


def error(request: 'HttpRequest'):
    """Raise an error, so that ModularHistory's server error page is rendered."""
    logging.info(f'Received request to trigger a server error: {request}')
    raise Exception('Raising an exception for testing purposes.')


_api = 'apps.{}.api.urls'.format  # noqa: P103

# fmt: off
urlpatterns = [
    # ---------------------------------
    # Admin
    # ---------------------------------
    path('admin_tools/', include('admin_tools.urls')),
    # path('admin/defender/', include('defender.urls')),  # defender admin  # TODO
    # https://github.com/dmpayton/django-admin-honeypot
    # https://github.com/dmpayton/django-admin-honeypot/issues/82
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),  # noqa: E800
    path(f'{settings.ADMIN_URL_PREFIX}/', admin_site.urls),
    # ---------------------------------
    # App URLs
    # ---------------------------------
    path('chat/', include('apps.chat.urls', namespace='chat')),
    path('api/donations/', include(_api('donations'), namespace='donations_api')),
    path('api/entities/', include(_api('entities'), namespace='entities_api')),
    path('api/forums/', include(_api('forums'), namespace='forums_api')),
    path('api/home/', include(_api('home'), namespace='home_api')),
    path('api/images/', include(_api('images'), namespace='images_api')),
    path('api/occurrences/', include(_api('occurrences'), namespace='occurrences_api')),
    path('api/places/', include(_api('places'), namespace='places_api')),
    path('api/propositions/', include(_api('propositions'), namespace='propositions_api')),
    path('api/quotes/', include(_api('quotes'), namespace='quotes_api')),
    path('api/redirects/', include(_api('redirects'), namespace='redirects_api')),
    path('api/search/', include(_api('search'), namespace='search_api')),
    path('api/sources/', include(_api('sources'), namespace='sources_api')),
    path('api/topics/', include(_api('topics'), namespace='topics_api')),
    path('api/users/', include(_api('users'), namespace='users_api')),
    path('api/flatpages/', include(_api('flatpages'), namespace='flatpages_api')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('api/collections/', include(_api('collections'), namespace='collections_api')),
    re_path(r'api/csrf/set/?', set_csrf_token),
    # ---------------------------------
    # Auth URLs
    # ---------------------------------
    path('api-auth/', include('rest_framework.urls')),
    # Note: This is required for internal auth requests.
    # https://github.com/iMerica/dj-rest-auth
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # ---------------------------------
    # Healthchecks
    # ---------------------------------
    path('watchman/', include('watchman.urls')),
    path('healthcheck/', bare_status),  # basic healthcheck
    path('ht/', include('health_check.urls')),
    # ---------------------------------
    # GraphQL (GraphIQL enabled during DEV, disabled during PROD)
    # ---------------------------------
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=False))),
    path('graphiql/', csrf_exempt(GraphQLView.as_view(graphiql=IS_DEV))),
    # ---------------------------------
    # Debugging & dev utilities
    # ---------------------------------
    # Error triggers:
    path('error', error),  # exception trigger
    path('errors/400', errors.bad_request),  # 400 trigger
    path('errors/403', errors.permission_denied),  # 403 trigger
    path('errors/404', errors.not_found),  # 404 trigger
    path('errors/500', errors.server_error),  # 500 trigger
    re_path(r'api/errors/(?P<error_code>\d+)/?$', errors.error),  # API error trigger
    # https://github.com/jazzband/django-silk
    path('silk/', include('silk.urls', namespace='silk')),
    # Graphviz model graph
    path('model-graph/', ModelGraphView.as_view()),
    # ---------------------------------
    # Sitemap
    # ---------------------------------
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # ---------------------------------
    # Miscellaneous third-party apps
    # ---------------------------------
    path('select2/', include('django_select2.urls')),
    path('trumbowyg/', include('trumbowyg.urls'))
]
# fmt: on

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#django.contrib.staticfiles.urls.staticfiles_urlpatterns  # noqa: E501
urlpatterns += staticfiles_urlpatterns()

handler400 = 'core.errors.bad_request'
handler403 = 'core.errors.permission_denied'
handler404 = 'core.errors.not_found'
handler500 = 'core.errors.server_error'
