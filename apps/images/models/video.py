from datetime import datetime, timedelta

import pafy
from django.core.exceptions import ValidationError
from django.db import models

from apps.images.models.media_model import MediaModel
from apps.topics.models.taggable import AbstractTopicRelation, TagsField
from core.fields.m2m_foreign_key import ManyToManyForeignKey

TITLE_MAX_LENGTH: int = 200
EMBED_CODE_MAX_LENGTH: int = 200


def get_video_fk(related_name: str) -> ManyToManyForeignKey:
    """Return a foreign key field referencing a video."""
    return ManyToManyForeignKey(
        to='images.Video',
        related_name=related_name,
        verbose_name='video',
    )


class VideoTopicRelation(AbstractTopicRelation):
    """A relationship between a video and a topic."""

    content_object = get_video_fk(related_name='topic_relations')


class Video(MediaModel):
    """A video."""

    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    url = models.URLField(null=True, unique=True)
    embed_code = models.CharField(max_length=EMBED_CODE_MAX_LENGTH)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    tags = TagsField(through=VideoTopicRelation)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        unique_together = ['title', 'url']

    def clean(self):
        """Prepare the video to be saved."""
        if not self.url:
            raise ValidationError('Video needs a link.')
        try:
            video = pafy.new(self.url)
            if not self.title:
                self.title = video.title
            if not self.duration:
                duration = datetime.strptime(video.duration, '%H:%M:%S')
                duration = timedelta(
                    hours=duration.hour, minutes=duration.minute, seconds=duration.second
                )
                self.duration = duration.seconds
        except Exception as error:  # TODO: Enable saving other kinds of videos
            raise Exception(
                f'Error: {error} \n Note: Non-YouTube videos are not yet supported.'
            )
