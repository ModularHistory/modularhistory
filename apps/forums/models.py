from django.db import models

from apps.users.models import User


class Thread(models.Model):
    """A Forum thread."""

    # creator = models.ForeignKey(User, on_delete=models.CASCADE)
    initial_post = models.ForeignKey("Post", on_delete=models.CASCADE)


class Post(models.Model):
    """A post in a forum thread"""

    content = models.TextField()
    title = models.CharField(max_length=140)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()

    parent_thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
