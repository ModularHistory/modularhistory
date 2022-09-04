from apps.places.models import Place
from apps.search.documents.base import InstantSearchDocumentFactory

PlaceInstantSearchDocument = InstantSearchDocumentFactory(
    model=Place,
    search_fields=['name'],
    field_kwargs={
        'name': {
            'attr': 'string',
        }
    },
)
