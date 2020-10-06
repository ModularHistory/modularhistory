import os
from urllib.parse import urljoin
from datetime import datetime
from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting


class LocalArtifactsStorage(FileSystemStorage):
    """Storage class for artifacts stored in the local filesystem."""

    location = setting('ARTIFACTS_ROOT')
    base_url = setting('ARTIFACTS_URL')

    def __init__(self, *args, **kwargs):
        """Instantiates LocalArtifactsStorage."""
        if not os.path.exists(self.location):
            # TODO: Make sure this does not break if writing permissions are missing
            os.makedirs(self.location)
        super().__init__(*args, **kwargs)


class MegaStorage(Storage):
    """TODO: add docstring."""

    def delete(self, name: str) -> None:
        return super().delete(name)

    def exists(self, name: str) -> bool:
        return super().exists(name)

    def get_accessed_time(self, name: str) -> datetime:
        return super().get_accessed_time(name)

    # TODO: https://docs.djangoproject.com/en/3.1/ref/files/storage/


class GoogleCloudArtifactsStorage(GoogleCloudStorage):
    """Storage class for artifacts stored in Google Cloud Storage."""

    bucket_name = setting('GS_ARTIFACTS_BUCKET_NAME')

    def url(self, name):
        """Gives the correct artifact URL (not the Google-generated url)."""
        return urljoin(settings.ARTIFACTS_URL, name)


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """Storage class for media files stored in Google Cloud Storage."""

    bucket_name = setting('GS_MEDIA_BUCKET_NAME')
    location = 'media'

    def url(self, name):
        """Gives the correct media URL (not the Google-generated url)."""
        return urljoin(settings.MEDIA_URL, name)


# TODO
class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """Storage class for static files stored in Google Cloud Storage."""

    bucket_name = setting('GS_STATIC_BUCKET_NAME')

    def url(self, name):
        """Gives the correct static URL (not the Google-generated URL)."""
        return urljoin(settings.STATIC_URL, name)
