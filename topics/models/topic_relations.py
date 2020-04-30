from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import CASCADE, ForeignKey

from history.models import (
    Model
)
from .models import Topic

if TYPE_CHECKING:
    pass


class TopicRelation(Model):
    """A relation to a topic (by any other model)."""
    topic = ForeignKey(Topic, related_name='topic_relations', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    weight = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1000)], default=500)

    class Meta:
        unique_together = ['topic', 'content_type', 'object_id']
        ordering = ['topic']

    @property
    def topic_pk(self) -> str:
        return str(self.topic.id)
