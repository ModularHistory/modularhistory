
from admin_auto_filters.views import AutocompleteJsonView
from django.db.models import Q
from meta.views import Meta

from apps.entities.models import Category, Entity  # , Person, Organization


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


# class DetailView(BaseDetailView):
#     """View depicting details of a specific entity."""

#     template_name = 'entities/detail.html'

#     def get_context_data(self, **kwargs):
#         """Return the context dictionary used to render the view."""
#         context = super().get_context_data(**kwargs)
#         entity = self.object
#         image: Optional[Dict[str, Any]] = entity.primary_image
#         img_src = image['src_url'] if image else None
#         context['meta'] = Meta(
#             title=entity.name,
#             description=f'Quotes by and historical information regarding {entity.name}',
#             keywords=[entity.name, 'quotes', *entity.tag_keys],
#             image=img_src,
#         )
#         return context
