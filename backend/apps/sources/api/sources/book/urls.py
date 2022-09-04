from rest_framework import routers

from apps.sources.api.sources.book import views

router = routers.DefaultRouter()
router.register('books', views.BookViewSet)
router.register('book-sections', views.SectionViewSet)
