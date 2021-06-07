from django.db import models

# Create your models here.


class Collection(models.Model):
    creator = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='collections',
    )
