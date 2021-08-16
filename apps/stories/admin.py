from apps.admin import ExtendedModelAdmin, StackedInline, admin_site
from apps.stories import models


class DownstreamStoriesInline(StackedInline):
    """Inline admin for a story's downstream stories."""

    verbose_name = 'downstream story'
    verbose_name_plural = 'downstream stories'
    model = models.StoryInspiration
    fk_name = 'upstream_story'
    extra = 0


class UpstreamStoriesInline(StackedInline):
    """Inline admin for a story's upstream stories."""

    verbose_name = 'upstream story'
    verbose_name_plural = 'upstream stories'
    model = models.StoryInspiration
    fk_name = 'downstream_story'
    extra = 0


class StoryElementsInline(StackedInline):
    """Inline admin for a story's elements."""

    verbose_name = 'story element'
    verbose_name_plural = 'story elements'
    model = models.StoryElement
    extra = 0


class StoryAdmin(ExtendedModelAdmin):
    """Admin for stories."""

    model = models.Story
    list_display = ['handle']
    list_filter = ['upstream_stories']
    search_fields = model.searchable_fields

    inlines = [
        DownstreamStoriesInline,
        UpstreamStoriesInline,
    ]


admin_site.register(models.Story, StoryAdmin)
