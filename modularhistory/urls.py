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

import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.views import serve
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from admin.model_admin import admin_site
from apps.search.views import SearchResultsView
from modularhistory import errors


def error(request):
    """Raise an error, so that ModularHistory's server error page is rendered."""
    logging.info(f'Received request to trigger a server error: {request}')
    raise Exception('Raising an exception for testing purposes.')


_api = 'apps.{}.api.urls'.format  # noqa: P103

# fmt: off
urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
    # Account
    path('account/', include(('apps.account.urls', 'account'), namespace='account')),
    # Admin
    path('admin/defender/', include('defender.urls')),  # defender admin
    path('admin/', include('massadmin.urls'), kwargs={'admin_site': admin_site}),
    path('admin/', admin_site.urls),
    # Chat
    path('chat/', include('apps.chat.urls', namespace='chat')),
    # Entities
    path('api/entities/', include(_api('entities'), namespace='entities_api')),
    path('entities/', include('apps.entities.urls', namespace='entities')),
    # Postulations
    path('api/postulations/', include(_api('postulations'), namespace='postulations_api')),
    path('facts/', include('apps.postulations.urls', namespace='facts')),
    path('postulations/', include('apps.postulations.urls', namespace='postulations')),
    # Images
    path('api/images/', include(_api('images'), namespace='images_api')),
    path('images/', include('apps.images.urls', namespace='images')),
    # Occurrences
    path('api/occurrences/', include(_api('occurrences'), namespace='occurrences_api')),
    path('occurrences/', include('apps.occurrences.urls', namespace='occurrences')),
    # Places
    path('api/places/', include(_api('places'), namespace='places_api')),
    path('places/', include(('apps.places.urls', 'places'), namespace='places')),
    path('locations/', include(('apps.places.urls', 'places'), namespace='locations')),
    # Quotes
    path('api/quotes/', include(_api('quotes'), namespace='quotes_api')),
    path('quotes/', include('apps.quotes.urls', namespace='quotes')),
    # Search
    path('api/search/', include(_api('search'), namespace='search_api')),
    path('search/', include('apps.search.urls', namespace='search')),
    re_path(r'search$', SearchResultsView.as_view(), name='search'),
    # Sources
    path('api/sources/', include(_api('sources'), namespace='sources_api')),
    path('sources/', include('apps.sources.urls', namespace='sources')),
    # Topics
    path('api/topics/', include(_api('topics'), namespace='topics_api')),
    path('topics/', include('apps.topics.urls', namespace='topics')),
    # Third-party apps
    path('api-auth/', include('rest_framework.urls')),
    path('martor/', include('martor.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('select2/', include('django_select2.urls')),
    path('tinymce/', include('tinymce.urls')),
    # Home
    path('', include('apps.home.urls')),
    # robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # Health check: https://github.com/KristianOellegaard/django-health-check
    path('ht/', include('health_check.urls')),
    # Debug toolbar: https://django-debug-toolbar.readthedocs.io/en/latest/
    path('__debug__', include(debug_toolbar.urls)),
    # Errors (for debugging)
    path('error', error),  # exception trigger
    path('errors/400', errors.bad_request),  # 400 trigger
    path('errors/403', errors.permission_denied),  # 403 trigger
    path('errors/404', errors.not_found),  # 404 trigger
    path('errors/500', errors.error),  # 500 trigger
    re_path(r'^(?P<path>favicon.ico)$', serve),
]
# fmt: on

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#django.contrib.staticfiles.urls.staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

handler400 = 'modularhistory.errors.bad_request'
handler403 = 'modularhistory.errors.permission_denied'
handler404 = 'modularhistory.errors.not_found'
handler500 = 'modularhistory.errors.error'
