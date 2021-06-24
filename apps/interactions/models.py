"""Models for the markup app."""

from difflib import ndiff

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.model import ExtendedModel


class ContentInteraction(ExtendedModel):
    """Abstract base model for content interactions."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        """Meta options for ContentInteraction."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        abstract = True


class FieldContentInteraction(ContentInteraction):
    """Abstract base model for field content interactions."""

    attribute_name = models.CharField(
        verbose_name=_('attribute name'),
        max_length=20,
        help_text='The name of the attribute that maps to the interacted content',
    )

    class Meta:
        """Meta options for FieldContentInteraction."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        abstract = True


class Edit(FieldContentInteraction):
    """An edit of some content."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='edits', on_delete=models.CASCADE
    )

    before = models.TextField(blank=False)
    after = models.TextField(blank=False)

    def __str__(self):
        """Return the comment's string representation."""
        return (
            f'{self.user}, {self.created_at}:\n'
            f'{ndiff(self.before.splitlines(), self.after.splitlines())}'
        )


class Comment(FieldContentInteraction):
    """A comment regarding some content."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE
    )

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()

    text = models.TextField(blank=False)

    def __str__(self):
        """Return the comment's string representation."""
        return f'{self.user}, {self.created_at}: {self.text}'


class Highlight(FieldContentInteraction):
    """Highlighted content."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='highlights', on_delete=models.CASCADE
    )

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()

    def __str__(self):
        """Return the comment's string representation."""
        return f'{self.user}, {self.updated_at}: {self.start}–{self.end}'
