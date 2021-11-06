import random

import pytest
from django.db.models import ForeignKey
from django.urls import reverse
from rest_framework.test import APIClient

from apps.moderation.models import Change, ContentContribution, ModeratedModel
from apps.users.models import User


def shuffled_copy(data, size=None):
    copy = data.copy()
    random.shuffle(copy)
    if size:
        return copy[:size]
    return copy


@pytest.mark.django_db()
@pytest.mark.usefixtures('api_client')
class ModerationApiTest:
    """Base moderation api test case."""

    # Only inheriting classes should publish tests.
    __test__ = False

    api_client: APIClient

    # api namespace, ex: quotes_api, entities_api
    api_name: str
    # api prefix, ex: quote, entity
    api_prefix: str

    contributor: User
    # verified moderated model to be used update/patch/delete tests
    verified_model: ModeratedModel

    # fields to be treated as relation fields TODO: could be improved to detect relation fields automatically via model._meta.get_field
    relation_fields = []
    # fields that won't be verified after creation/update/patch
    uncheckable_fields = []
    # test data to be used for creation and update/patch respectively
    test_data: dict
    updated_test_data: dict

    # extra args to be passed to the APIClient.post/put/patch methods in #api_moderation_view_test
    moderation_api_request_extra_kwargs = {}

    def _test_api_view_get(self, view, url_kwargs=None, status_code=200):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        response = self.api_client.get(path)
        assert response.status_code == status_code, 'Incorrect status code'

    def _test_api_moderation_view(
        self,
        data,
        view='api-root',
        url_kwargs=None,
        change_status_code=200,
        method='post',
        object_id=None,
    ):
        if url_kwargs is None:
            url_kwargs = {}
        if object_id:
            url_kwargs.update({'pk_or_slug': object_id})
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        response = self.api_client.post(
            path, data, **self.moderation_api_request_extra_kwargs
        )
        assert response.status_code == 401, 'Deny creation without authentication'
        self.api_client.force_authenticate(self.contributor)
        api_request = getattr(self.api_client, method)
        response = api_request(path, data, **self.moderation_api_request_extra_kwargs)
        self.api_client.logout()
        assert (
            response.status_code == change_status_code
        ), f'Incorrect change status code. {method} {path} returned: {response.data}'
        if response.data and 'id' in response.data:
            object_id = response.data.get('id')
        created_change = Change.objects.get(
            initiator=self.contributor,
            object_id=object_id,
        )
        contributions = ContentContribution.objects.filter(
            contributor=self.contributor, change_id=created_change
        )
        # TODO: find out why multiple contributions are created
        assert contributions.count() > 0, 'No contributions were created for a change'
        return response.data, created_change, contributions

    def _test_api_moderation_change(self, request_params):
        response, change, contribution = self._test_api_moderation_view(**request_params)
        data_fields = request_params.get('data').items()
        for field_name, value in data_fields:
            if field_name in self.relation_fields:
                changed_object_field = getattr(change.changed_object, field_name)
                is_foreign_key = isinstance(
                    change.changed_object._meta.get_field(field_name), ForeignKey
                )
                if is_foreign_key:
                    assert (
                        changed_object_field.id == value
                    ), f'{field_name} was not changed correctly'
                else:
                    relations = changed_object_field.values_list('id', flat=True)
                    for value_item in value:
                        assert (
                            value_item in relations
                        ), f'{field_name} does not contain {value_item}'
            elif field_name not in self.uncheckable_fields:
                assert (
                    getattr(change.changed_object, field_name) == value
                ), f'{field_name} was not changed correctly'

    def test_api_list(self):
        """Test the moderated listing API."""
        self._test_api_view_get(f'{self.api_prefix}-list')

    def test_api_detail(self):
        """Test the moderated detail API."""
        self._test_api_view_get(
            f'{self.api_prefix}-detail', url_kwargs={'pk_or_slug': self.verified_model.id}
        )

    def test_api_create(self):
        """Test the moderated creation API."""
        request_params = {'data': self.test_data, 'change_status_code': 201}
        self._test_api_moderation_change(request_params)

    def test_api_update(self):
        """Test the moderated update API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_model.id,
            'view': f'{self.api_prefix}-detail',
            'method': 'put',
        }
        self._test_api_moderation_change(request_params)

    def test_api_patch(self):
        """Test the moderated patch API."""
        request_params = {
            'data': self.updated_test_data,
            'object_id': self.verified_model.id,
            'view': f'{self.api_prefix}-detail',
            'method': 'patch',
        }
        self._test_api_moderation_change(request_params)

    def test_api_delete(self):
        """Test the quotes delete API."""
        request_params = {
            'data': {},
            'view': f'{self.api_prefix}-detail',
            'object_id': self.verified_model.id,
            'method': 'delete',
            'change_status_code': 204,
        }
        response, change, contribution = self._test_api_moderation_view(**request_params)
        assert change.changed_object.deleted is not None, 'Deletion change was not created'
