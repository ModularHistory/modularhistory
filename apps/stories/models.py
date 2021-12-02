"""Model classes for stories (myths, legends, etc.)."""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import Serializer

from apps.sources.models.citation import AbstractCitation
from apps.sources.models.model_with_sources import ModelWithSources
from apps.stories.serializers import StorySerializer
from core.fields.html_field import HTMLField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.model import ExtendedModel

HANDLE_MAX_LENGTH = 40


class Citation(AbstractCitation):
    """A relationship between a story and a source."""

    content_object = ManyToManyForeignKey(
        to='stories.Story',
        related_name='citations',
        verbose_name='story',
    )


class Story(ModelWithSources):
    """A story."""

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
    sources = models.ManyToManyField(
        to='sources.Source',
        related_name='%(class)s_citations',
        through=Citation,
        blank=True,
        verbose_name=_('sources'),
    )

    searchable_fields = ['handle', 'description']
    slug_base_fields = ('handle',)

    @classmethod
    def get_serializer(self) -> Serializer:
        """Return the serializer for the entity."""
        from apps.stories.serializers import StorySerializer

        return StorySerializer

    def __str__(self) -> str:
        """Return the fact's string representation."""
        return self.handle


class StoryElement(ExtendedModel):
    """An element or component of a story."""

    key = models.CharField(max_length=HANDLE_MAX_LENGTH, unique=True)

    def __str__(self) -> str:
        """Return the story element's string representation."""
        return self.key


class StoryElementInclusion(ExtendedModel):
    """An element or component of a story."""

    story = models.ForeignKey(
        to='stories.Story',
        on_delete=models.CASCADE,
    )
    story_element = models.ForeignKey(
        to='stories.StoryElement',
        on_delete=models.CASCADE,
    )
    justification = HTMLField(
        blank=True,
        paragraphed=True,
    )

    def __str__(self) -> str:
        """Return the story element's string representation."""
        return f'{self.story} << {self.story_element}'


class StoryInspiration(ExtendedModel):
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

    def __str__(self) -> str:
        """Return the story element's string representation."""
        return f'{self.upstream_story.handle} --> {self.downstream_story.handle}'
