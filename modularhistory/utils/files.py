import logging
import os
import re
from copy import deepcopy
from os.path import isfile, join
from pprint import pformat
from typing import Dict, List


def envsubst(input_file) -> str:
    """Python implementation of envsubst."""
    with open(input_file, 'r') as base:
        content_after = content_before = base.read()
        for match in re.finditer(r'\$\{?(.+?)\}?', content_before):
            env_var = match.group(1)
            env_var_value = os.getenv(env_var)
            content_after = content_before.replace(match.group(0), env_var_value or '')
    return content_after


def get_extensionless_filenames(path):
    """Return a list of extensionless filenames at the path."""
    return [
        filename.replace('.pdf', '')
        for filename in os.listdir(path)
        if isfile(join(path, filename))
    ]


DuplicatedFiles = Dict[str, List[str]]


# TODO
def get_duplicated_files(path) -> DuplicatedFiles:
    """Return a tuple of names of duplicated files at the given path."""
    reference_filenames = get_extensionless_filenames(path)
    filenames = deepcopy(reference_filenames)
    duplicated_files: DuplicatedFiles = {}
    for potential_duplicate_filename in filenames:
        reference_filenames.remove(potential_duplicate_filename)
        for reference_filename in reference_filenames:
            is_duplicate = (
                reference_filename in potential_duplicate_filename
                and potential_duplicate_filename.startswith(reference_filename[:3])
            )
            if is_duplicate:
                duplicate_files = duplicated_files.get(reference_filename) or []
                duplicate_files.append(potential_duplicate_filename)
                duplicated_files[reference_filename] = duplicate_files
    return duplicated_files


def relativize(path: str):
    """Convert the path to a relative path."""
    return join('.', path)


def upload_to_mega(filepath: str, account: str = 'default'):
    """Upload a file to Mega."""
    from modularhistory.storage.mega_storage import mega_clients  # noqa: E402

    mega_client = mega_clients[account]
    filename = os.path.basename(filepath)
    logging.info(f'Pushing {filepath} to Mega ({account}) ...')
    extant_file = mega_client.find(filename, exclude_deleted=True)
    if extant_file:
        logging.info(f'Deleting extant backup ({extant_file}) ...')
        try:
            mega_client.delete(filename)
        except Exception as err:
            logging.error(f'Unable to delete {filename} from Mega; {err}')
    result = mega_client.upload(filepath)
    logging.info(f'Upload result: {pformat(result)}')
    uploaded_file = mega_client.find(filename)
    if not uploaded_file:
        raise Exception(
            f'Could not find {filename} in Mega ({account}) after uploading.'
        )
    return uploaded_file
