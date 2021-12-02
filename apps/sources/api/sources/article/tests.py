"""Tests for the articles api."""

import pytest
from django.contrib.contenttypes.models import ContentType

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest
from apps.sources.api.serializers import SourceAttributionSerializer
from apps.sources.api.sources.publication.serializers import PublicationSerializer
from apps.sources.factories import ArticleFactory, PublicationFactory
from apps.sources.models import Article
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory


class ArticleApiTest(ModerationApiTest):
    """Test the articles api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'article'
    api_path_suffix = 'articles'

    @pytest.fixture(autouse=True)
    def data(self, db: None):
        self.contributor = UserFactory.create()
        self.content_type = ContentType.objects.get_for_model(Article)
        verified_article: Article = ArticleFactory.create(verified=True)
        self.attributee_ids = [EntityFactory.create().id for _ in range(4)]
        self.topic_ids = [TopicFactory.create().id for _ in range(4)]
        self.publications = [PublicationFactory.create() for _ in range(2)]
        Article.attributees.through.objects.create(
            source=verified_article,
            attributee_id=self.attributee_ids[3],
            verified=True,
        )
        Article.tags.through.objects.create(
            content_object=verified_article,
            topic_id=self.topic_ids[3],
            verified=True,
        )
        self.verified_model = verified_article
        self.uncheckable_fields = [
            'date',
            'end_date',
            'original_publication_date',
        ]
        self.relation_fields = ['publication', 'attributions', 'source_containments', 'tags']

    @pytest.fixture()
    def data_for_creation(self, db: None, data: None):
        return {
            'title': 'Test article',
            'page_number': 23,
            'end_page_number': 1,
            'editors': 'Some editor',
            'number': 1,
            'volume': 2,
            'original_publication_date': '0001-01-01T01:01:20.086200Z',
            'date': '2017-01-01 01:01:20.086202',
            'end_date': '2020-01-01 01:01:20.086202',
            'publication': PublicationSerializer(self.publications[0]).data,
            'attributions': [
                SourceAttributionSerializer(
                    Article.attributees.through(
                        attributee_id=id,
                    )
                ).data
                for id in self.attributee_ids[:2]
            ],
            'tags': self.topic_ids[:2],
        }

    @pytest.fixture()
    def data_for_update(self, db: None, data: None):
        return {
            'title': 'UPDATED Test article',
            'page_number': 25,
            'end_page_number': 12,
            'editors': 'UPDATED Some editor',
            'number': 10,
            'volume': 20,
            'original_publication_date': '0005-01-01T01:01:20.086200Z',
            'date': '2027-01-01 01:01:20',
            'publication': PublicationSerializer(self.publications[1]).data,
            'attributions': [
                SourceAttributionSerializer(
                    Article.attributees.through(
                        attributee_id=id,
                    )
                ).data
                for id in self.attributee_ids[1:]
            ],
            'tags': self.topic_ids[1:],
        }
