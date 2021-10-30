from django.db import models
from django.utils.timezone import now

from apps.users.models import User
from core.models.module import Module


class Thread(models.Model):
    """A forum thread."""

    # creator = models.ForeignKey(User, on_delete=models.CASCADE)  # noqa: E800
    initial_post = models.ForeignKey('Post', null=True, on_delete=models.CASCADE)
    updated_date = models.DateTimeField(default=now)

    def __str__(self) -> str:
        """Return the thread's string representation."""
        return f'{self.initial_post}'


class Post(models.Model):
    """A post in a forum thread."""

    content = models.TextField()
    title = models.CharField(max_length=140)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()

    parent_thread = models.ForeignKey(Thread, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return the post's string representation."""
        return f'{self.content}'
