from django.contrib.admin import TabularInline, StackedInline
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    # StackedPolymorphicInline,
    PolymorphicInlineSupportMixin
)

from admin import admin_site, Admin
from topics.models import OccurrenceTopicRelation
from . import models


class LocationsInline(TabularInline):
    model = models.Occurrence.locations.through
    extra = 1


class ImagesInline(StackedInline):
    model = models.Occurrence.images.through
    extra = 1


class RelatedQuotesInline(StackedInline):
    model = models.Occurrence.related_quotes.through
    extra = 1


class RelatedTopicsInline(StackedInline):
    model = OccurrenceTopicRelation
    extra = 1


class SourceReferencesInline(StackedInline):
    model = models.Occurrence.sources.through
    extra = 1


class InvolvedEntitiesInline(TabularInline):
    model = models.Occurrence.involved_entities.through
    extra = 1


class YearAdmin(Admin):
    list_display = ('years_before_present', 'common_era', 'nickname')
    # list_filter = ('',)
    search_fields = models.Year.searchable_fields
    ordering = ('-years_before_present', 'common_era')


# class DurationInline(StackedPolymorphicInline):
#     model = models.Duration
#
#     class DurationInline(StackedPolymorphicInline.Child):
#         model = models.Duration
#
#     class EpisodeInline(StackedPolymorphicInline.Child):
#         model = models.Episode
#
#     child_inlines = (
#         DurationInline,
#         EpisodeInline
#     )


class OccurrenceModelAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, Admin):
    base_model = models.Occurrence
    child_models = [
        models.Duration,
        models.Episode,
    ]
    list_display = ('summary', 'description__truncated', 'pretty_year', 'date', 'polymorphic_ctype', 'topic_tags')
    list_filter = ('involved_entities', 'locations', 'year')
    search_fields = models.Occurrence.searchable_fields + ['year__common_era']
    ordering = ('year', 'date')

    inlines = [
        RelatedQuotesInline, InvolvedEntitiesInline,
        LocationsInline, ImagesInline,
        SourceReferencesInline,
        RelatedTopicsInline
    ]


class DurationModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Occurrence
    inlines = OccurrenceModelAdmin.inlines


class EpisodeModelAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin, Admin):
    base_model = models.Occurrence
    inlines = OccurrenceModelAdmin.inlines


admin_site.register(models.Occurrence, OccurrenceModelAdmin)
admin_site.register(models.Duration, DurationModelAdmin)
admin_site.register(models.Episode, EpisodeModelAdmin)
admin_site.register(models.Year, YearAdmin)
# admin_site.register(models.OccurrenceLocation)
# admin_site.register(models.OccurrenceEntityInvolvement)
# admin_site.register(models.SourceReference)
