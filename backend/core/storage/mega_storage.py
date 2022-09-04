# import logging
# import os
# import tempfile
# from datetime import datetime
# from pprint import pformat
# from typing import IO, Any, Optional

# import requests
# from django.conf import settings
# from django.core.exceptions import SuspiciousFileOperation
# from django.core.files import File
# from django.core.files.storage import Storage
# from django.utils.crypto import get_random_string
# from mega import Mega
# from mega.mega import (
#     AES,
#     Counter,
#     RequestError,
#     a32_to_str,
#     base64_to_a32,
#     base64_url_decode,
#     decrypt_attr,
#     get_chunks,
#     str_to_a32,
# )

# from core.constants.environments import Environments
# from core.environment import IS_PROD

# SIXTEEN = 16
# THIRTY_TWO = 32
# SIXTY_FOUR = 64
# ONE_TWENTY_EIGHT = 128

# a, g, n, p, s = 'a', 'g', 'n', 'p', 's'  # noqa: WPS111
# file_url_key = g
# file_size_key = s


# class MegaClient(Mega):
#     """Wrapper for Mega."""

#     def get_file_info(self, url: str) -> os.stat_result:
#         """Get a file's OS info from its public URL."""
#         return os.stat(self.get_temporary_file(url).name)

#     def get_url_from_name(self, name: str) -> str:
#         """Get a file's public URL from its name."""
#         return self.get_link(self.find(name))

#     def get_temporary_file(self, url: str, mode: str = 'w+b'):
#         """Download a file by its public URL."""
#         file_stream, key, iv, counter, file_size, meta_mac = self._get_file_stream(url)
#         aes = AES.new(key, AES.MODE_CTR, counter=counter)
#         mac_str = '\0' * SIXTEEN
#         mac_encryptor = AES.new(key, AES.MODE_CBC, mac_str.encode('utf8'))
#         with tempfile.NamedTemporaryFile(
#             mode=mode, prefix='megapy_', delete=False
#         ) as temp_output_file:
#             encryptor = AES.new(key, AES.MODE_CBC, iv)
#             for _chunk_start, chunk_size in get_chunks(file_size):
#                 chunk = aes.decrypt(file_stream.read(chunk_size))
#                 temp_output_file.write(chunk)
#                 mac_str = _encrypt_chunk(chunk, encryptor, mac_encryptor, file_size)
#                 st_size = os.stat(temp_output_file.name).st_size
#                 logging.info(f'{st_size} of {file_size} downloaded')
#             file_mac = str_to_a32(mac_str)
#             # check mac integrity
#             new_meta_mac = (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3])
#             if new_meta_mac != meta_mac:
#                 raise ValueError('Mismatched mac')
#             return temp_output_file

#     def _get_file_stream(self, url: str) -> tuple[Any, ...]:
#         """Return a file stream and other values needed by get_temporary_file."""
#         is_public = True
#         path = self._parse_url(url).split('!')
#         file_handle, file_key = path[0], path[1]
#         if is_public:
#             file_key = base64_to_a32(file_key)
#             file_data = self._api_request({a: g, g: 1, p: file_handle})
#         else:
#             file_data = self._api_request({a: g, g: 1, n: file_handle})
#         keys = (
#             file_key[0] ^ file_key[4],
#             file_key[1] ^ file_key[5],
#             file_key[2] ^ file_key[6],
#             file_key[3] ^ file_key[7],
#         )
#         iv = file_key[4:6] + (0, 0)
#         meta_mac = file_key[6:8]
#         file_url = file_data.get(file_url_key, None)
#         if not file_url:
#             raise RequestError('File is not accessible anymore')
#         file_size = file_data[file_size_key]
#         attributes = decrypt_attr(base64_url_decode(file_data['at']), keys)
#         file_name = attributes[n]
#         logging.info(f'Getting file stream for {file_name}...')
#         input_file = requests.get(file_url, stream=True).raw
#         key_string = a32_to_str(keys)
#         iv_string = a32_to_str([iv[0], iv[1], iv[0], iv[1]])
#         counter = Counter.new(
#             ONE_TWENTY_EIGHT,
#             initial_value=((iv[0] << THIRTY_TWO) + iv[1]) << SIXTY_FOUR,
#         )
#         return input_file, key_string, iv_string, counter, file_size, meta_mac


# def _encrypt_chunk(chunk, encryptor, mac_encryptor, file_size):
#     for index in range(0, len(chunk) - SIXTEEN, SIXTEEN):
#         block = chunk[index : index + SIXTEEN]
#         encryptor.encrypt(block)
#     # fix for files under 16 bytes failing
#     if file_size > SIXTEEN:
#         index += SIXTEEN
#     else:
#         index = 0
#     block = chunk[index : index + SIXTEEN]
#     if len(block) % SIXTEEN:
#         block += b'\0' * (SIXTEEN - (len(block) % SIXTEEN))
#     return mac_encryptor.encrypt(encryptor.encrypt(block))


# try:
#     mega_client = MegaClient().login(settings.MEGA_USERNAME, settings.MEGA_PASSWORD)
#     mega_user = mega_client.get_user()
#     logging.info(f'Obtained Mega client for {settings.MEGA_USERNAME}: {pformat(mega_user)}')
# except Exception as err:
#     logging.error(f'Failed to initialize Mega client: {err}')
#     mega_client = None


# mega_clients = {'default': mega_client}
# if IS_PROD and mega_client:
#     mega_clients[Environments.DEV] = mega_client
#     mega_user = mega_client.get_user()
# else:
#     mega_clients[Environments.DEV] = mega_client


# class MegaStorage(Storage):
#     """Storage class for Mega.nz cloud storage."""

#     def delete(self, name: str):
#         """
#         Delete the file referenced by name.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.delete
#         """
#         mega_client.delete(name)

#     def exists(self, name: str) -> bool:
#         """
#         Return whether a file with the given name already exists in the storage system.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.exists
#         """
#         return mega_client.find(name) is not None

#     def get_accessed_time(self, name: str) -> datetime:
#         """
#         Return a datetime of the last accessed time of the file.

#         If USE_TZ is True, returns an aware datetime;
#         otherwise returns a naive datetime in the local timezone.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.get_accessed_time
#         """
#         url = mega_client.get_url_from_name(name)
#         return datetime.fromtimestamp(mega_client.get_file_info(url).st_atime)

#     def get_alternative_name(self, file_root, file_ext):
#         """
#         Return an alternative filename with additional characters.

#         Current implementation adds an underscore and a random 7-character
#         alphanumeric string (before the file extension) to the filename.
#         """
#         return f'{file_root}_{get_random_string(7)}{file_ext}'

#     def get_available_name(self, name: str, max_length: Optional[int] = 100) -> str:
#         """
#         Return a filename (based on the name parameter) that is available on Mega.

#         If a file with name already exists, get_alternative_name() is called
#         to obtain an alternative name.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.get_available_name
#         """
#         # TODO
#         dir_name, file_name = os.path.split(name)
#         file_root, file_ext = os.path.splitext(file_name)
#         # If the filename already exists, generate an alternative filename
#         # until it doesn't exist.
#         # Truncate original name if required, so the new filename does not
#         # exceed the max_length.
#         while self.exists(name) or (max_length and len(name) > max_length):
#             # file_ext includes the dot.
#             name = os.path.join(dir_name, self.get_alternative_name(file_root, file_ext))
#             if max_length is None:
#                 continue
#             # Truncate file_root if max_length exceeded.
#             truncation = len(name) - max_length
#             if truncation > 0:
#                 file_root = file_root[:-truncation]
#                 # Entire file_root was truncated in attempt to find an available filename.
#                 if not file_root:
#                     raise SuspiciousFileOperation(
#                         'Storage can not find an available filename for "%s". '
#                         'Please make sure that the corresponding file field '
#                         'allows sufficient "max_length".' % name
#                     )
#                 name = os.path.join(dir_name, self.get_alternative_name(file_root, file_ext))
#         return name

#     def get_created_time(self, name: str) -> datetime:
#         """
#         Return the datetime of the file's creation.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.get_created_time
#         """
#         url = mega_client.get_url_from_name(name)
#         return datetime.fromtimestamp(mega_client.get_file_info(url).st_ctime)

#     def get_modified_time(self, name: str) -> datetime:
#         """
#         Return the datetime of the file's last modification.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.get_modified_time
#         """
#         url = mega_client.get_url_from_name(name)
#         return datetime.fromtimestamp(mega_client.get_file_info(url).st_mtime)

#     def generate_filename(self, filename: str) -> str:
#         """
#         Validate the filename by calling get_valid_name().

#         This method returns a filename to be passed to the save() method.

#         The filename argument may include a path as returned by FileField.upload_to.
#         In that case, the path won’t be passed to get_valid_name() but will be
#         prepended back to the resulting name.

#         The default implementation uses os.path operations.
#         Override this method if that’s not appropriate for your storage.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.generate_filename
#         """
#         # TODO
#         dirname, filename = os.path.split(filename)
#         return os.path.normpath(os.path.join(dirname, self.get_valid_name(filename)))

#     def listdir(self, path: str) -> tuple[list[str], list[str]]:
#         """
#         List the contents of the specified path.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.listdir
#         """
#         # TODO
#         raise NotImplementedError

#     def open(self, name: str, mode: str = 'rb') -> File:  # noqa: WPS125
#         """
#         Open the file given by name.

#         Although the returned file is guaranteed to be a File object,
#         it might actually be some subclass. In the case of remote file storage,
#         this means that reading/writing could be quite slow.  Be warned.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.open
#         """
#         url = mega_client.get_url_from_name(name)
#         return mega_client.get_temporary_file(url, mode=mode)

#     def save(
#         self,
#         name: Optional[str],
#         content: IO[Any],  # noqa: WPS110
#         max_length: Optional[int] = None,
#     ) -> str:
#         """
#         Save a new file using the storage system, preferably with the name specified.

#         If there already exists a file with this name name,
#         the storage system may modify the filename as necessary to get a unique name.
#         The actual name of the stored file will be returned.

#         The max_length argument is passed along to get_available_name().

#         The content argument must be an instance of django.core.files.File
#         or a file-like object that can be wrapped in File.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.save
#         """
#         # TODO: improve implementation to agree with docstring
#         with tempfile.NamedTemporaryFile(
#             mode='w+b', prefix='megapy_', delete=False
#         ) as temp_file:
#             # write content
#             upload_response = mega_client.upload(
#                 temp_file.name, dest=None, dest_filename=name  # TODO
#             )
#         return upload_response

#     def size(self, name: str) -> int:
#         """
#         Return the total size, in bytes, of the file referenced by name.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.size
#         """
#         url = mega_client.get_url_from_name(name)
#         return mega_client.get_file_info(url).st_size

#     def url(self, name: Optional[str]) -> str:
#         """
#         Return the URL where the contents of the file referenced by name can be accessed.

#         https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.Storage.url
#         """
#         return mega_client.get_url_from_name(name)
