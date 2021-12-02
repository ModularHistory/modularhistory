from apps.sources.api.sources.article.serializers import ArticleSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Article


class ArticleViewSet(SourceViewSet):
    """API endpoint for viewing and editing article sources."""

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
