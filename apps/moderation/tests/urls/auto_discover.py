from django.conf import settings
from django.conf.urls import handler500, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

handler500

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
].extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
