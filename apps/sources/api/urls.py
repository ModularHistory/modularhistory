from django.urls import include, path
from rest_framework import routers

from apps.sources.api import views
from apps.sources.api.sources.article.urls import router as article_router
from apps.sources.api.sources.book.urls import router as book_router
from apps.sources.api.sources.document.urls import router as documents_router
from apps.sources.api.sources.entry.urls import router as entry_router
from apps.sources.api.sources.file.urls import router as file_router
from apps.sources.api.sources.film.urls import router as film_router
from apps.sources.api.sources.interview.urls import router as interview_router
from apps.sources.api.sources.piece.urls import router as piece_router
from apps.sources.api.sources.publication.urls import router as publications_router
from apps.sources.api.sources.report.urls import router as report_router
from apps.sources.api.sources.speech.urls import router as speech_router

router = routers.DefaultRouter()
router.register('sources', views.SourceViewSet)

app_name = 'sources'

urlpatterns = [
    path('', include(entry_router.urls)),
    path('', include(film_router.urls)),
    path('', include(book_router.urls)),
    path('', include(speech_router.urls)),
    path('', include(report_router.urls)),
    path('', include(piece_router.urls)),
    path('', include(interview_router.urls)),
    path('', include(article_router.urls)),
    path('', include(documents_router.urls)),
    path('', include(publications_router.urls)),
    path('', include(file_router.urls)),
    path('', include(router.urls)),
]
