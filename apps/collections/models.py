from django.db import models

# Create your models here.


class Collection(models.Model):
    """A user-created collection."""

    creator = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='collections',
    )

    def __str__(self) -> str:
        return f'collection created by {self.creator}'
