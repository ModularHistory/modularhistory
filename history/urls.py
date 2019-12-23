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
from django.apps import apps
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('occurrences/', include('occurrences.urls')),
    path('people/', include('people.urls')),
    path('places/', include('places.urls')),
    path('quotes/', include('quotes.urls')),
    path('sources/', include('sources.urls')),
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('django_mako_plus.urls')),
]

# manually register the polls app with DMP
apps.get_app_config('django_mako_plus').register_app('occurrences')
apps.get_app_config('django_mako_plus').register_app('people')
