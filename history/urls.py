"""history URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from admin import admin_site
from search.views import SearchResultsView


def error(request):
    """Raise an error, so that ModularHistory's server error page is rendered."""
    print(f'Received request to trigger a server error: {request}')
    raise Exception('Raising an exception for testing purposes.')


urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
    path('nested_admin/', include('nested_admin.urls')),
    path('admin/', include('massadmin.urls'), kwargs={'admin_site': admin_site}),
    path('admin/', admin_site.urls),
    path('occurrences/', include(('occurrences.urls', 'occurrences'), namespace='occurrences')),
    path('entities/', include(('entities.urls', 'entities'), namespace='entities')),
    path('images/', include(('images.urls', 'images'), namespace='images')),
    path('places/', include(('places.urls', 'places'), namespace='places')),
    path('quotes/', include(('quotes.urls', 'quotes'), namespace='quotes')),
    path('sources/', include(('sources.urls', 'sources'), namespace='sources')),
    path('topics/', include(('topics.urls', 'topics'), namespace='topics')),
    re_path(r'search/?', SearchResultsView.as_view(), name='search'),
    path('search/', include(('search.urls', 'search'), namespace='search')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('account/', include(('account.urls', 'account'), namespace='account')),
    path('api-auth/', include('rest_framework.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('select2/', include('django_select2.urls')),
    path('', include('home.urls')),
    path('error', error),  # error trigger (for testing purposes)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__', include(debug_toolbar.urls))
    ] + urlpatterns
