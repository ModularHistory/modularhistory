"""Models for the markup app."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from account.models import User
from modularhistory.models import Model
from difflib import ndiff


class GenericContentInteraction(Model):
    """Abstract base model for content interactions."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    attribute_name = models.CharField(
        max_length=20,
        help_text='The name of the attribute that maps to the interacted content',
    )

    class Meta:
        abstract = True


class Edit(GenericContentInteraction):
    """An edit of some content."""

    user = models.ForeignKey(User, related_name='edits', on_delete=models.CASCADE)

    before = models.TextField(blank=False)
    after = models.TextField(blank=False)

    def __str__(self):
        """Return the comment's string representation."""
        return (
            f'{self.user}, {self.created_at}:\n'
            f'{ndiff(self.before.splitlines(), self.after.splitlines())}'
        )


class Comment(GenericContentInteraction):
    """A comment regarding some content."""

    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()

    text = models.TextField(blank=False)

    def __str__(self):
        """Return the comment's string representation."""
        return f'{self.user}, {self.created_at}: {self.text}'


class Highlight(GenericContentInteraction):
    """Highlighted content."""

    user = models.ForeignKey(User, related_name='highlights', on_delete=models.CASCADE)

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()

    def __str__(self):
        """Return the comment's string representation."""
        return f'{self.user}, {self.updated_at}: {self.start}–{self.end}'
