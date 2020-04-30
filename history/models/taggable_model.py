from typing import List, Optional, TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import QuerySet
from django.utils.safestring import SafeText, mark_safe

from .base_model import Model

if TYPE_CHECKING:
    from topics.models import Topic


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""
    tags = GenericRelation('topics.TopicRelation')

    class Meta:
        abstract = True

    @property
    def has_tags(self) -> bool:
        return bool(self.related_topics)

    @property
    def related_topics(self) -> List['Topic']:
        if not self.tags.exists():
            return []
        related_topics = [tag.topic for tag in self.tags.all()]
        return related_topics

    @property
    def tags_string(self) -> Optional[str]:
        if self.has_tags:
            related_topics = [topic.key for topic in self.related_topics]
            if related_topics:
                return ', '.join(related_topics)
        return None

    @property
    def tags_html(self) -> Optional[SafeText]:
        if self.has_tags:
            return mark_safe(
                ' '.join([
                    f'<li class="topic-tag"><a>{topic.key}</a></li>'
                    for topic in self.related_topics
                ])
            )
        return None
