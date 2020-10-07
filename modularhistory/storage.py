import os
from datetime import datetime
from typing import Any, IO, List, Optional, Tuple
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import File, FileSystemStorage, Storage
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
        """
        Deletes the file referenced by name.

        If deletion is not supported on the target storage system this will raise NotImplementedError instead.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.delete
        """
        return super().delete(name)

    def exists(self, name: str) -> bool:
        """
        Returns True if a file referenced by the given name already exists in the storage system,
        or False if the name is available for a new file.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.exists
        """
        return super().exists(name)

    def get_accessed_time(self, name: str) -> datetime:
        """
        Returns a datetime of the last accessed time of the file.

        For storage systems unable to return the last accessed time this will raise NotImplementedError.

        If USE_TZ is True, returns an aware datetime, otherwise returns a naive datetime in the local timezone.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.get_accessed_time
        """
        return super().get_accessed_time(name)

    def get_available_name(self, name: str, max_length: Optional[int] = 100) -> str:
        """
        Returns a filename (based on the name parameter) that is available on Mega.

        If a file with name already exists, get_alternative_name() is called to obtain an alternative name.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.get_available_name
        """
        return super().get_available_name(name, max_length)

    def get_created_time(self, name: str) -> datetime:
        """
        Returns a datetime of the creation time of the file.

        For storage systems unable to return the creation time this will raise NotImplementedError.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.get_created_time
        """
        return super().get_created_time(name)

    def get_modified_time(self, name: str) -> datetime:
        """
        Returns a datetime of the last modified time of the file.

        For storage systems unable to return the last modified time this will raise NotImplementedError.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.get_modified_time
        """
        return super().get_modified_time(name)

    def get_valid_name(self, name: str) -> str:
        """
        Returns a filename based on the name parameter that’s suitable for use on the target storage system.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.get_valid_name
        """
        return super().get_valid_name(name)

    def generate_filename(self, filename: str) -> str:
        """
        Validates the filename by calling get_valid_name() and returns a filename to be passed to the save() method.

        The filename argument may include a path as returned by FileField.upload_to. In that case,
        the path won’t be passed to get_valid_name() but will be prepended back to the resulting name.

        The default implementation uses os.path operations.
        Override this method if that’s not appropriate for your storage.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.generate_filename
        """
        return super().generate_filename(filename)

    def listdir(self, path: str) -> Tuple[List[str], List[str]]:
        """
        Lists the contents of the specified path.

        Returns a 2-tuple of lists; the first item being directories, the second item being files.
        For storage systems that aren’t able to provide such a listing, this will raise a NotImplementedError instead.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.listdir
        """
        return super().listdir(path)

    def open(self, name: str, mode: str = 'rb') -> File:
        """
        Opens the file given by name.

        Note that although the returned file is guaranteed to be a File object, it might actually be some subclass.
        In the case of remote file storage this means that reading/writing could be quite slow, so be warned.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.open
        """
        return super().open(name, mode)

    def path(self, name: str) -> str:
        """
        The local filesystem path where the file can be opened using Python’s standard open().

        For storage systems that aren’t accessible from the local filesystem,
        this will raise NotImplementedError instead.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.path
        """
        return super().path(name)

    def save(self, name: Optional[str], content: IO[Any], max_length: Optional[int] = None) -> str:
        """
        Saves a new file using the storage system, preferably with the name specified.

        If there already exists a file with this name name,
        the storage system may modify the filename as necessary to get a unique name.
        The actual name of the stored file will be returned.

        The max_length argument is passed along to get_available_name().

        The content argument must be an instance of django.core.files.File
        or a file-like object that can be wrapped in File.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.save
        """
        return super().save(name, content, max_length)

    def size(self, name: str) -> int:
        """
        Returns the total size, in bytes, of the file referenced by name.

        For storage systems that aren’t able to return the file size this will raise NotImplementedError instead.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.size
        """
        return super().size(name)

    def url(self, name: Optional[str]) -> str:
        """
        Returns the URL where the contents of the file referenced by name can be accessed.

        For storage systems that don’t support access by URL this will raise NotImplementedError instead.

        https://docs.djangoproject.com/en/3.1/ref/files/storage/#django.core.files.storage.Storage.url
        """
        return super().url(name)

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
