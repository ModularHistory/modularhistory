# type: ignore
# TODO: remove above line after fixing typechecking
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import CASCADE, ForeignKey

from history.models import Model
from topics.models.topics import Topic

MAX_WEIGHT = 1000
DEFAULT_WEIGHT = MAX_WEIGHT / 2


class TopicRelation(Model):
    """A relation to a topic (by any other model)."""

    topic = ForeignKey(Topic, related_name='topic_relations', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    weight = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(MAX_WEIGHT)], default=DEFAULT_WEIGHT)

    class Meta:
        unique_together = ['topic', 'content_type', 'object_id']
        ordering = ['topic']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return str(self.topic)

    @property
    def topic_pk(self) -> str:
        """TODO: write docstring."""
        return str(self.topic.id)
