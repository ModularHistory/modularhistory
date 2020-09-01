# type: ignore
# TODO: remove above line after fixing typechecking
from django.db import models
from django.db.models import ForeignKey, CASCADE

from history.fields import ArrayField
from history.models import (
    Model
)

parts_of_speech = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Classification(Model):
    name = models.CharField(max_length=100, unique=True)
    part_of_speech = models.CharField(
        max_length=9, choices=parts_of_speech,
        default='adj'
    )
    aliases = ArrayField(
        models.CharField(max_length=100),
        null=True, blank=True
    )
    parent = ForeignKey(
        'self', related_name='children',
        null=True, blank=True,
        on_delete=CASCADE
    )
    weight = models.PositiveSmallIntegerField(default=1, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
