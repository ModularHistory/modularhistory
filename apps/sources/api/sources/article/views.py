from typing import TYPE_CHECKING

from apps.sources.api.sources.article.serializers import ArticleDrfSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Article

if TYPE_CHECKING:
    from rest_framework.request import Request


class ArticleViewSet(SourceViewSet):
    """API endpoint for viewing and editing article sources."""

    queryset = Article.objects.all()
    serializer_class = ArticleDrfSerializer
