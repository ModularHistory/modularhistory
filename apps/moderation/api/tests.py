import logging
import random

import pytest
from django.db.models import ForeignKey
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apps.moderation.models import Change, ContentContribution
from apps.users.models import User


def shuffled_copy(data, size=None):
    copy = data.copy()
    random.shuffle(copy)
    if size:
        return copy[:size]
    return copy


class ModerationApiTest(APITestCase):
    """Base moderation api test case."""

    api_client = APIClient()

    # api namespace
    api_name: str

    contributor: User

    relation_fields = []
    uncheckable_fields = []
    test_data: dict
    updated_test_data: dict

    def api_view_get_test(self, view, url_kwargs=None, status_code=200):
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)
        response = self.api_client.get(path)

        self.assertEqual(
            response.status_code, status_code, 'Response does not have expected status'
        )

    def api_moderation_view_test(
        self,
        data,
        view='api-root',
        url_kwargs=None,
        change_status_code=200,
        method='post',
        format='json',
        object_id=None,
    ):
        if url_kwargs is None:
            url_kwargs = {}
        if object_id:
            url_kwargs.update({'pk_or_slug': object_id})
        path = reverse(f'{self.api_name}:{view}', kwargs=url_kwargs)

        self.assertEqual(
            self.api_client.post(path, data, format=format).status_code,
            401,
            'Deny creation without authentication',
        )

        self.api_client.force_authenticate(self.contributor)

        api_request = getattr(self.api_client, method)
        response = api_request(path, data, format=format)

        if response.status_code != change_status_code:
            logging.error(f'{method} {path} returned: {response.data}')

        self.api_client.logout()

        self.assertEqual(
            response.status_code, change_status_code, 'Change status code is not correct'
        )

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
        self.assertGreater(
            contributions.count(),
            0,
            'Incorrect count of Contributions were created for a change',
        )

        return response.data, created_change, contributions

    def api_moderation_change_test(self, request_params):
        (response, change, contribution) = self.api_moderation_view_test(**request_params)
        data_fields = request_params.get('data').items()
        for field_name, value in data_fields:
            if field_name in self.relation_fields:
                changed_object_field = getattr(change.changed_object, field_name)

                is_foreign_key = isinstance(
                    change.changed_object._meta.get_field(field_name), ForeignKey
                )
                if is_foreign_key:
                    self.assertEqual(
                        changed_object_field.id,
                        value,
                        f'{field_name} was not changed correctly',
                    )
                else:
                    relations = changed_object_field.values_list('id', flat=True)
                    for value_item in value:
                        self.assertIn(
                            value_item,
                            relations,
                            f'{field_name} does not contain {value_item}',
                        )
            elif field_name not in self.uncheckable_fields:
                self.assertEqual(
                    getattr(change.changed_object, field_name),
                    value,
                    f'{field_name} field was not updated correctly',
                )
