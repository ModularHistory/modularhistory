"""Model classes for stories (myths, legends, etc.)."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.model_with_sources import ModelWithSources
from apps.stories.serializers import StorySerializer
from core.fields import HTMLField
from core.models.model import Model

HANDLE_MAX_LENGTH = 40


class Story(ModelWithSources):
    """A postulation."""

    handle = models.CharField(max_length=HANDLE_MAX_LENGTH, unique=True)
    description = HTMLField(
        verbose_name=_('description'), null=True, blank=True, paragraphed=True
    )
    elements = models.ManyToManyField(
        to='stories.StoryElement',
        through='stories.StoryElementInclusion',
        related_name='stories',
        verbose_name=_('story elements'),
    )
    upstream_stories = models.ManyToManyField(
        to='self',
        through='stories.StoryInspiration',
        related_name='downstream_stories',
        symmetrical=False,
        verbose_name=_('upstream stories'),
    )

    searchable_fields = ['handle', 'description']
    serializer = StorySerializer
    slug_base_field = 'handle'

    def __str__(self) -> str:
        """Return the fact's string representation."""
        return self.summary.text


class StoryElement(Model):
    """An element or component of a story."""

    key = models.CharField(max_length=HANDLE_MAX_LENGTH, unique=True)

    def __str__(self) -> str:
        """Return the story element's string representation."""
        return self.key


class StoryElementInclusion(Model):
    """An element or component of a story."""

    story = models.ForeignKey(to='stories.Story', on_delete=models.CASCADE)
    story_element = models.ForeignKey(
        to='stories.StoryElement', on_delete=models.CASCADE
    )
    justification = HTMLField(null=True, blank=True, paragraphed=True)

    def __str__(self) -> str:
        """Return the story element's string representation."""
        return f'{self.story} << {self.story_element}'


class StoryInspiration(Model):
    """An inspiration of a story by another story."""

    upstream_story = models.ForeignKey(
        to='stories.Story',
        on_delete=models.CASCADE,
        related_name='inspirations_out',
    )
    downstream_story = models.ForeignKey(
        to='stories.Story',
        on_delete=models.CASCADE,
        related_name='inspirations_in',
    )
