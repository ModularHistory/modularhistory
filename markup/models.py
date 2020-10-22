"""Models for the markup app."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from account.models import User
from modularhistory.models import Model


class Highlight(Model):
    """Highlighted content."""

    agent = models.ForeignKey(User, related_name='highlights', on_delete=models.CASCADE)
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        """Return the comment's string representation."""
        return f'{self.agent}, {self.updated_at}: {self.start}–{self.end}'


class Comment(Model):
    """A comment regarding some content."""

    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        """Return the comment's string representation."""
        return f'{self.author}, {self.created_at}: {self.text}'
