from typing import Any, Dict, Optional

from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from django.views import generic
from meta.views import Meta
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.entities.models import Category, Entity  # , Person, Organization
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


class EntitySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self):
        """Return the filtered queryset."""
        queryset = Entity.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term)
                | Q(unabbreviated_name__icontains=term)
                | Q(aliases__icontains=term)
            )
        return queryset


class EntityCategorySearchView(AutocompleteJsonView):
    """Used by autocomplete widget in admin."""

    def get_queryset(self):
        """Return the filtered queryset."""
        queryset = Category.objects.all()
        term = self.term
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) | Q(aliases__icontains=term)
            )
        return queryset


class IndexView(generic.ListView):
    """View depicting all entities."""

    model = Entity
    template_name = 'entities/index.html'
    paginate_by = 20
    context_object_name = 'entities'

    def get_queryset(self):
        """Return the last five published questions."""
        print('skjdfklsdjfljsljfljlsdjljf')
        return Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore


class BaseDetailView(generic.detail.DetailView):
    """Base class for entity detail views."""

    model = Entity
    context_object_name = 'entity'
    query_pk_and_slug = True

    object: Entity


class DetailView(BaseDetailView):
    """View depicting details of a specific entity."""

    template_name = 'entities/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.object
        image: Optional[Dict[str, Any]] = entity.primary_image
        img_src = image['src_url'] if image else None
        context['meta'] = Meta(
            title=entity.name,
            description=f'Quotes by and historical information regarding {entity.name}',
            keywords=[entity.name, 'quotes', *entity.tag_keys],
            image=img_src,
        )
        return context


class DetailPartView(BaseDetailView):
    """Partial view depicting details of a specific entity."""

    template_name = 'entities/_detail.html'
