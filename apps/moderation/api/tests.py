import json
import random
from typing import TYPE_CHECKING, Callable, Optional, Union

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey
from django.urls import reverse
from rest_framework.test import APIClient

from apps.moderation.models import Change, ContentContribution, ModeratedModel
from apps.users.models import User

if TYPE_CHECKING:
    from django.db.models.manager import Manager
    from rest_framework.response import Response


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
    # api path suffix for nested endpoints like Sources, ex: articles
    # reverse urls will be rewritten to include this suffix if it doesn't contain already
    api_path_suffix: str = None

    contributor: User
    # verified moderated model to be used update/patch/delete tests
    verified_model: ModeratedModel
    content_type: ContentType

    # fields to be treated as relation fields
    # TODO: could be improved to detect relation fields automatically via model._meta.get_field
    relation_fields = []
    # fields that won't be verified after creation/update/patch
    # TODO: usually date fields are not checkable, find a way to check them or detect them automatically
    uncheckable_fields = []
    # test data to be used for creation and update/patch respectively
    test_data: dict
    updated_test_data: dict

    def _test_api_view_get(self, view, url_kwargs=None, status_code=200):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        # TODO: refactor this (also in _test_api_moderation_view).
        # Force request path to include API path suffix.
        if self.api_path_suffix and self.api_path_suffix not in path:
            path += self.api_path_suffix + '/'
        response = self.api_client.get(path)
        assert response.status_code == status_code, 'Incorrect status code'

    def _test_api_moderation_view(
        self,
        data: dict,
        view: str = 'api-root',
        url_kwargs=None,
        change_status_code: int = 200,
        method: str = 'post',
        object_id: Optional[int] = None,
    ):
        if url_kwargs is None:
            url_kwargs = {}
        if object_id:
            url_kwargs.update({'pk_or_slug': object_id})
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        # Force request path to include API path suffix.
        if self.api_path_suffix and self.api_path_suffix not in path:
            path += self.api_path_suffix + '/'
        json_data: str = json.dumps(data)
        request_kwargs = {
            'path': path,
            'data': json_data,
            'content_type': 'application/json',
        }
        api_request: Callable = getattr(self.api_client, method)
        response: 'Response' = api_request(**request_kwargs)
        assert (
            response.status_code == 401
        ), 'Request without authentication should have been denied.'
        self.api_client.force_authenticate(self.contributor)
        from pprint import pformat

        try:
            response = api_request(**request_kwargs)
        except Exception as err:
            raise Exception(pformat(data.get('attributions')) + '\n' + str(err))
        self.api_client.logout()
        if response.status_code != change_status_code:
            raise Exception(f'Incorrect change status code: {response.data}')
        assert (
            response.status_code == change_status_code
        ), f'Incorrect change status code: {response.data}'
        if response.data and 'pk' in response.data:
            object_id = response.data['pk']
        assert Change.objects.filter(
            object_id=object_id, content_type=self.content_type
        ).exists(), f'No change for {self.content_type} with {object_id=} was found: {Change.objects.all()}'
        created_change = Change.objects.get(
            initiator=self.contributor,
            object_id=object_id,
            content_type=self.content_type,
        )
        contributions = ContentContribution.objects.filter(
            contributor=self.contributor, change_id=created_change
        )
        assert contributions.exists(), 'No contribution was created for a change.'
        assert contributions.count() == 1, 'Multiple contributions were created for a change.'
        return response.data, created_change, contributions

    def _test_api_moderation_change(self, data: dict, **request_params):
        response, change, contribution = self._test_api_moderation_view(
            data, **request_params
        )
        for field_name, value in data.items():
            if field_name in self.relation_fields:
                changed_object_field = getattr(change.changed_object, field_name)
                is_foreign_key = isinstance(
                    change.changed_object._meta.get_field(field_name), ForeignKey
                )
                if is_foreign_key:
                    id = value.get('pk') if isinstance(value, dict) else value
                    assert (
                        changed_object_field.id == id
                    ), f'{field_name} was not changed correctly.'
                else:
                    related_manager: 'Manager' = changed_object_field
                    item: Union[dict, int]
                    for item in value:
                        if isinstance(item, dict):
                            # TODO: confirm this is a relation to a `through` model
                            id = item.pop('pk')
                            assert related_manager.model.all_objects.filter(
                                **item
                            ).exists(), (
                                f'{field_name} ({related_manager}) does not contain {item}.'
                            )
                        else:
                            # TODO: confirm this is a direct m2m relation (ignoring the `through` model)
                            id = item
                            assert related_manager.model.objects.filter(
                                pk=id
                            ).exists(), (
                                f'{field_name} ({related_manager}) does not contain {id}.'
                            )
            elif field_name == 'id':  # TODO
                assert (
                    change.changed_object.pk == value
                ), f'{field_name} was not changed correctly.'
            elif field_name not in self.uncheckable_fields:
                assert (
                    getattr(change.changed_object, field_name) == value
                ), f'{field_name} was not changed correctly.'

    def test_api_list(self):
        """Test the moderated listing API."""
        self._test_api_view_get(f'{self.api_prefix}-list')

    def test_api_detail(self):
        """Test the moderated detail API."""
        self._test_api_view_get(
            f'{self.api_prefix}-detail', url_kwargs={'pk_or_slug': self.verified_model.pk}
        )

    def test_api_create(self, data_for_creation: dict):
        """Test the moderated creation API."""
        self._test_api_moderation_change(
            data=data_for_creation,
            change_status_code=201,
        )

    def test_api_update(self, data_for_update: dict):
        """Test the moderated update API."""
        self._test_api_moderation_change(
            data=data_for_update,
            view=f'{self.api_prefix}-detail',
            object_id=self.verified_model.pk,
            method='put',
        )

    def test_api_patch(self, data_for_update: dict):
        """Test the moderated patch API."""
        self._test_api_moderation_change(
            data=data_for_update,
            view=f'{self.api_prefix}-detail',
            object_id=self.verified_model.pk,
            method='patch',
        )

    def test_api_delete(self):
        """Test the quotes delete API."""
        response, change, contribution = self._test_api_moderation_view(
            data={},
            view=f'{self.api_prefix}-detail',
            object_id=self.verified_model.pk,
            method='delete',
            change_status_code=204,
        )
        assert change.changed_object.deleted is not None, 'Deletion change was not created'
