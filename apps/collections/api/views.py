from typing import TYPE_CHECKING

from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.collections.api.serializers import CollectionSerializer
from apps.collections.models import Collection

if TYPE_CHECKING:
    from rest_framework.request import Request


class CollectionViewSet(ModelViewSet):
    """API endpoint for viewing and editing collections."""

    queryset = Collection.objects.all()
    lookup_field = 'slug'
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CollectionEditItemsView(APIView):
    """Edits My Collection items."""

    my_collection_name = _('My Collection')

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: 'Request', *args, **kwargs):
        """Apply items to the collection."""
        data = request.data
        sources = data.get('sources', [])
        propositions = data.get('propositions', [])
        entities = data.get('entities', [])
        quotes = data.get('quotes', [])

        collection_args = {'title': self.my_collection_name, 'creator': request.user}
        try:
            collection = Collection.objects.get(**collection_args)
        except Collection.DoesNotExist:
            collection = Collection.objects.create(**collection_args)

        self.apply_items(
            collection,
            {
                'sources': sources,
                'propositions': propositions,
                'entities': entities,
                'quotes': quotes,
            },
        )

        return Response(CollectionSerializer(collection).data)

    def apply_items(self, collection: Collection, items):
        raise NotImplementedError


class CollectionAddItemsView(CollectionEditItemsView):
    """Add items to the collection."""

    def apply_items(self, collection: Collection, items):
        try:
            collection.sources.add(*items['sources'])
            collection.propositions.add(*items['propositions'])
            collection.entities.add(*items['entities'])
            collection.quotes.add(*items['quotes'])
        except IntegrityError:
            raise ValidationError('Some items were not found in the database')


class CollectionRemoveItemsView(CollectionEditItemsView):
    """Remove items from the collection."""

    def apply_items(self, collection: Collection, items):
        collection.sources.remove(*items['sources'])
        collection.propositions.remove(*items['propositions'])
        collection.entities.remove(*items['entities'])
        collection.quotes.remove(*items['quotes'])
