"""Tests for the articles api."""

import pytest

from apps.entities.factories import EntityFactory
from apps.moderation.api.tests import ModerationApiTest
from apps.sources.factories import ArticleFactory, PublicationFactory
from apps.topics.factories import TopicFactory
from apps.users.factories import UserFactory

# TODO: something weird is going on with relation tests
# after creating test entities with ids = [1, 2, 3, 4]
# we set request.cls.test_data.attributees to ids = [3, 4]
# and expect to changed_object.attributees == [3, 4] in #ModerationApiTest.api_moderation_change_test
# it actually returns [2, 1] or [1]
# expected [3, 4] attributees are actually inserted into db, confirmed by:
# from apps.sources.models import SourceAttribution
# print(f"All SourceAttributions: {SourceAttribution.objects.values('source_id', 'attributee_id', 'pk')}")


@pytest.fixture(scope='class')
def articles_api_test_data(request):
    request.cls.contributor = UserFactory.create()

    article = ArticleFactory.create(verified=True)

    attributees = [EntityFactory.create(verified=True).id for _ in range(4)]
    tags = [TopicFactory.create(verified=True).id for _ in range(4)]
    publications = [PublicationFactory.create(verified=True).id for _ in range(2)]

    # article.attributees.set(attributees, size=2)
    # article.tags.set(shuffled_copy(tags, size=2))

    article.attributees.set([attributees[3]])
    article.tags.set([tags[3]])

    request.cls.verified_model = article
    request.cls.uncheckable_fields = ['date', 'end_date', 'original_publication_date']
    request.cls.relation_fields = ['publication', 'attributees', 'tags']
    request.cls.test_data = {
        'title': 'Test article',
        'page_number': 23,
        'end_page_number': 1,
        'editors': 'Some editor',
        'number': 1,
        'volume': 2,
        'original_publication_date': '0001-01-01T01:01:20.086200Z',
        'date': '2017-01-01 01:01:20.086202',
        'end_date': '2020-01-01 01:01:20.086202',
        'publication': publications[0],
        'attributees': attributees[:2],
        'tags': tags[:2],
        # 'attributees': [3, 4],
    }
    request.cls.updated_test_data = {
        'title': 'UPDATED Test article',
        'page_number': 25,
        'end_page_number': 12,
        'editors': 'UPDATED Some editor',
        'number': 10,
        'volume': 20,
        'original_publication_date': '0005-01-01T01:01:20.086200Z',
        'date': '2027-01-01 01:01:20',
        'publication': publications[1],
        'attributees': attributees[1:],
        'tags': tags[1:],
    }


@pytest.mark.usefixtures('articles_api_test_data')
class ArticleApiTest(ModerationApiTest):
    """Test the articles api."""

    __test__ = True
    api_name = 'sources_api'
    api_prefix = 'article'
    api_path_suffix = 'articles'
