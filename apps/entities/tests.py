"""Tests for the entities app."""

import pytest
from django.test import Client

from apps.entities.models import Person
from core.tests import TestSuite


@pytest.mark.django_db()
class EntitiesTestSuite(TestSuite):
    """Tests for the admin app."""

    def test_entity_query(self):
        """Verify pages have 200 status."""
        client = Client()
        name = 'Albert Einstein'
        person: Person = Person.objects.create(name=name)
        # fmt: off
        query = '''
        {
            entity(slug: "%s") {
                name
                slug
                description
                serializedImages
                model
                adminUrl
            }
        }
        ''' % person.slug
        # fmt: on
        response = client.post('/graphql/', {'query': query.strip()})
        assert response.status_code == 200
        response_content = f'{response.content}'
        assert '"entity"' in response_content
        assert f'"name":"{name}"' in response_content
