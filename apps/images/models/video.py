import pafy
from django.core.exceptions import ValidationError
from django.db import models

# from modularhistory.settings import mega  # TODO
from apps.images.models.media_model import MediaModel

TITLE_MAX_LENGTH: int = 200
EMBED_CODE_MAX_LENGTH: int = 200


class Video(MediaModel):
    """A video."""

    title = models.CharField(max_length=TITLE_MAX_LENGTH, null=True)
    url = models.URLField(null=True, unique=True)
    embed_code = models.CharField(max_length=EMBED_CODE_MAX_LENGTH, null=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        """
        Meta options for Video.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

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
                self.duration = video.duration
        except Exception as error:  # TODO: Enable saving other kinds of videos
            raise Exception(
                f'Error: {error} \n Note: Non-YouTube videos are not yet supported.'
            )
