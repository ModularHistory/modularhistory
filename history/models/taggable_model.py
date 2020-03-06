from typing import Any, List, Optional

from django.utils.safestring import SafeText, mark_safe

from topics.models import Topic
from .base_model import Model


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""
    related_topics: Any

    class Meta:
        abstract = True

    @property
    def _related_topics(self) -> Optional[List[Topic]]:
        if self.related_topics and len(self.related_topics.all()):
            return list(self.related_topics.all())
        return None

    @property
    def topic_tags(self) -> Optional[SafeText]:
        if self._related_topics:
            return mark_safe(' '.join([f'<li class="topic-tag"><a>{topic.key}</a></li>'
                                       for topic in self._related_topics]))
        return None
