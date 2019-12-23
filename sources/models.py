from django.db import models
from tinymce.models import HTMLField


class Source(models.Model):
    """A source for quotes or historical information."""
    text = models.CharField(max_length=1000, unique=True)
    description = HTMLField(null=True, blank=True)
    year = models.ForeignKey('occurrences.Year', related_name='publications', on_delete=models.PROTECT)
    date = models.DateTimeField(null=True, blank=True)
    # publication = models.OneToOneField(Occurrence, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.text}'
