import json
import random
from typing import TYPE_CHECKING, Callable, Optional, Union

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey, ManyToOneRel
from django.db.models.fields.related import RelatedField
from django.urls import reverse
from rest_framework.test import APIClient

from apps.dates.structures import HistoricDateTime
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

    # fields that won't be verified after creation/update/patch
    uncheckable_fields = []
    # test data to be used for creation and update/patch respectively
    test_data: dict
    updated_test_data: dict

    def build_api_path(self, view, url_kwargs):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        if self.api_path_suffix and self.api_path_suffix not in path:
            path += self.api_path_suffix + '/'
        return path

    def _test_api_view_get(self, view, url_kwargs=None, status_code=200):
        path = self.build_api_path(view, url_kwargs)
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
        path = self.build_api_path(view, url_kwargs)
        api_request: Callable = getattr(self.api_client, method)
        request_kwargs = {
            'path': path,
            'data': json.dumps(data),
            'content_type': 'application/json',
        }

        # test without auth first
        response: 'Response' = api_request(**request_kwargs)
        assert (
            response.status_code == 401
        ), 'Request without authentication should have been denied.'

        # then temporarily login as contributor to test moderation
        self.api_client.force_authenticate(self.contributor)
        response = api_request(**request_kwargs)
        self.api_client.logout()

        assert (
            response.status_code == change_status_code
        ), f'Incorrect change status code: {response.data}'

        content_type = ContentType.objects.get_for_model(self.verified_model)
        if response.data and 'pk' in response.data:
            object_id = response.data['pk']

        assert Change.objects.filter(
            object_id=object_id, content_type=content_type
        ).exists(), f'No change for {content_type} with {object_id=} was found: {Change.objects.all()}'

        created_change = Change.objects.get(
            initiator=self.contributor,
            object_id=object_id,
            content_type=content_type,
        )
        contributions = ContentContribution.objects.filter(
            contributor=self.contributor, change_id=created_change
        )
        assert contributions.exists(), 'No contribution was created for a change.'
        assert contributions.count() == 1, 'Multiple contributions were created for a change.'
        return response.data, created_change, contributions

    def _test_api_moderation_changes(self, data: dict, **request_params):
        response, change, contribution = self._test_api_moderation_view(
            data, **request_params
        )
        for field_name, value in data.items():
            changed_object_field = getattr(change.changed_object, field_name)
            field_info = change.changed_object._meta.get_field(field_name)
            if self._test_moderated_field_relation_changes(
                changed_object_field, field_name, field_info, value
            ):
                pass
            elif field_name == 'id':  # TODO
                assert (
                    change.changed_object.pk == value
                ), f'{field_name} was not changed correctly.'
            elif isinstance(changed_object_field, HistoricDateTime):
                assert changed_object_field == HistoricDateTime.from_iso(
                    value
                ), f'HistoricDateTime {field_name} was not changed correctly.'
            elif field_name not in self.uncheckable_fields:
                assert (
                    changed_object_field == value
                ), f'{field_name} was not changed correctly.'

    def _test_moderated_field_relation_changes(
        self, changed_object_field, field_name: str, field_info, value
    ):
        is_foreign_key = isinstance(field_info, ForeignKey)
        is_related_field = isinstance(field_info, RelatedField) or isinstance(
            field_info, ManyToOneRel
        )

        if is_foreign_key:
            pk = value.get('pk') if isinstance(value, dict) else value
            assert changed_object_field.id == pk, f'{field_name} was not changed correctly.'
        elif is_related_field:
            related_manager: 'Manager' = changed_object_field
            item: Union[dict, int]
            for item in value:
                if isinstance(item, dict):
                    # TODO: confirm this is a relation to a `through` model
                    assert related_manager.model.all_objects.filter(
                        **item
                    ).exists(), f'{field_name} ({related_manager}) does not contain {item}.'
                else:
                    # TODO: confirm this is a direct m2m relation (ignoring the `through` model)
                    pk = item
                    assert related_manager.model.objects.filter(
                        pk=pk
                    ).exists(), f'{field_name} ({related_manager}) does not contain {pk}.'

        return is_foreign_key or is_related_field

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
        self._test_api_moderation_changes(
            data=data_for_creation,
            change_status_code=201,
        )

    def test_api_update(self, data_for_update: dict):
        """Test the moderated update API."""
        self._test_api_moderation_changes(
            data=data_for_update,
            view=f'{self.api_prefix}-detail',
            object_id=self.verified_model.pk,
            method='put',
        )

    def test_api_patch(self, data_for_update: dict):
        """Test the moderated patch API."""
        self._test_api_moderation_changes(
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
