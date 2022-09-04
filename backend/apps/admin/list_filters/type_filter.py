from typing import TYPE_CHECKING, Any, Optional, Sequence

from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from polymorphic.admin import PolymorphicParentModelAdmin

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest
    from polymorphic.models import PolymorphicModel
    from typedmodels.models import TypedModel


class ContentTypeFilter(SimpleListFilter):
    """Filter by content type."""

    title = 'content type'
    parameter_name = 'content_type_id'

    def __init__(
        self,
        request: 'HttpRequest',
        params: dict[str, str],
        model: type['Model'],
        model_admin: Any,
    ) -> None:
        self.model = model
        super().__init__(request, params, model, model_admin)

    def lookups(self, request: 'HttpRequest', model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        if self.model:
            ids = (
                self.model.objects.order_by(self.parameter_name)
                .values_list(self.parameter_name, flat=True)
                .distinct()
            )
            return [(ct.id, f'{ct.model}') for ct in ContentType.objects.filter(id__in=ids)]
        return super().lookups(request, model_admin)

    def queryset(self, request: 'HttpRequest', queryset):
        """Return the queryset filtered by type."""
        content_type_id = self.value()
        if not content_type_id:
            return queryset
        return queryset.filter(**{self.parameter_name: content_type_id})


class PolymorphicContentTypeFilter(ContentTypeFilter):
    """Filters sources by type."""

    parameter_name = 'polymorphic_ctype_id'
    model_options: Optional[Sequence[type['PolymorphicModel']]] = None

    def lookups(self, request: 'HttpRequest', model_admin: PolymorphicParentModelAdmin):
        """Return an iterable of tuples (value, verbose value)."""
        if self.model_options:
            lookups = []
            for option in self.model_options:
                ct = ContentType.objects.get_for_model(option)
                lookups.append((ct.id, f'{ct.model}'))
            return lookups
        else:
            return sorted(
                {
                    (instance.polymorphic_ctype_id, instance.ctype_name)
                    for instance in model_admin.get_queryset(request)
                },
                key=lambda ctype_tuple: ctype_tuple[1],
            )


class TypeFilter(SimpleListFilter):
    """Filters sources by type."""

    title = 'type'
    parameter_name = 'type'
    base_model: type['TypedModel']

    def lookups(self, request: 'HttpRequest', model_admin):
        """Return an iterable of tuples (value, verbose value)."""
        return self.base_model._meta.get_field('type').choices

    def queryset(self, request: 'HttpRequest', queryset):
        """Return the queryset filtered by type."""
        type_value = self.value()
        if not type_value:
            return queryset
        return queryset.filter(type=type_value)
