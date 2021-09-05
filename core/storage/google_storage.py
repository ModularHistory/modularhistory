import logging
from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import ValidationError
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """Storage class for media files stored in Google Cloud Storage."""

    bucket_name = setting('GS_MEDIA_BUCKET_NAME')
    location = 'media'

    def url(self, name):
        """Give the correct media URL (not the Google-generated url)."""
        return urljoin(settings.MEDIA_URL, name)

    def open(self, name: str, mode: str = 'rb'):
        """Retrieve the specified file from storage."""
        try:
            logging.debug(f'Opening {name} with GoogleCloudMediaFileStorage...')
            super().open(name, mode)
            logging.debug(f'Successfully opened {name}.')
        except Exception as err:
            raise ValueError(f'Attempting to open "{name}" resulted in {err}')

    def save(self, name, content, max_length=None):
        """Save a media file to Google Cloud."""
        try:
            super().save(name, content, max_length)
        except Exception as err:
            raise ValidationError(f'Attempting to save file "{name}" resulted in {err}')


# TODO
class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """Storage class for static files stored in Google Cloud Storage."""

    bucket_name = setting('GS_STATIC_BUCKET_NAME')

    def url(self, name):
        """Give the correct static URL (not the Google-generated URL)."""
        return urljoin(settings.STATIC_URL, name)
