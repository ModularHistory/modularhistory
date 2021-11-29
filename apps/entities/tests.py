"""Tests for the entities app."""

import json

import pytest
from graphene_django.utils.testing import graphql_query

from apps.entities.factories import EntityFactory
from apps.entities.models.entity import Entity
from core.tests import TestSuite


@pytest.fixture()
def client_query(client):
    """GraphQL query helper."""

    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client)

    return func


@pytest.mark.django_db()
class EntitiesTestSuite(TestSuite):
    """Tests for the entities app."""

    def test_entity_query(self, client_query):
        """Verify pages have 200 status."""
        name = 'Albert Einstein'
        entity: Entity = EntityFactory.create(name=name)
        # fmt: off
        query = '''
        {
            entity(slug: "%s") {
                name
                slug
                description
                cachedImages
                model
                adminUrl
            }
        }
        ''' % entity.slug
        # fmt: on
        response = client_query(query)
        assert response
        assert response.status_code == 200
        content = json.loads(response.content)
        assert 'errors' not in content
        assert 'entity' in f'{content}'
