from django.db import models
from tinymce.models import HTMLField


class Person(models.Model):
    """A person"""
    name = models.CharField(max_length=100)
    description = HTMLField(null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    death_date = models.DateTimeField(null=True, blank=True)
    is_living = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'People'

    def __str__(self):
        return f'{self.name}'
