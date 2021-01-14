from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.entities.models import Entity
from apps.entities.serializers import EntitySerializer


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class EntityListAPIView(ListAPIView):
    """API view for listing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
