"""Admin for the quotes app."""

from typing import Optional

from admin import TabularInline
from quotes import models


class AttributeesInline(TabularInline):
    """Inline admin for a quote's attributees."""

    model = models.QuoteAttribution
    autocomplete_fields = ['attributee']

    sortable_field_name = 'position'

    def get_extra(
        self, request, model_instance: Optional[models.Quote] = None, **kwargs
    ):
        """TODO: add docstring."""
        if model_instance and model_instance.attributees.count():
            return 0
        return 1


class BitesInline(TabularInline):
    """Inline admin for a quote's bites."""

    model = models.QuoteBite
    extra = 0


# TODO: try to get this reverse relationship working
# class OccurrencesInline(GenericTabularInline):
#     model = models.QuoteRelation
#     # readonly_fields = ['']
#     # autocomplete_fields = ['occurrence']
#     verbose_name = 'occurrence'
#     verbose_name_plural = 'occurrences'
#
#     def get_queryset(self, request):
#         # qs: QuerySet = super().get_queryset(request)
#         pk = re.search(r'/(\d+)/', request.path).group(1)
#         ct = ContentType.objects.get_for_model(Occurrence)
#         qs: QuerySet = models.QuoteRelation.objects.filter(
#             quote_id=pk,
#             content_type_id=ct.id
#         )
#         return qs.filter(content_type_id=ct.id)
#
#     def get_extra(self, request, model_instance=None, **kwargs):
#         if len(self.get_queryset(request)):
#             return 0
#         return 1
