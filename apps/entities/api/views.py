from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.entities.models import Entity
from apps.entities.serializers import EntityPartialDictSerializer, EntitySerializer
from core.pagination import VariableSizePagination


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer


class EntityListAPIView(ListAPIView):
    """API view for listing entities."""

    permission_classes = [permissions.AllowAny]
    serializer_class = EntitySerializer
    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore


class EntityPartialAPIView(ListAPIView):
    """API view for listing client-selected attributes of entities.

    Desired attributes are specified with the `attributes` query
    parameter, and only these attributes are retrieved.
    The client can use the `page_size` parameter to guarantee all
    results are in a single response.
    """

    pagination_class = VariableSizePagination
    permission_classes = [permissions.AllowAny]
    serializer_class = EntityPartialDictSerializer
    allowed_attributes = {'pk', 'id', 'name'}

    def get_queryset(self):
        # get attributes to retrieve from query parameters
        attributes = set(self.request.query_params.getlist('attributes'))
        if not attributes:
            return []

        # check for any disallowed attributes
        bad_attributes = attributes - self.allowed_attributes
        if bad_attributes:
            raise ValidationError(
                f'Requested disallowed attribute(s): {bad_attributes}'
            )

        return Entity.objects.values(*attributes)
