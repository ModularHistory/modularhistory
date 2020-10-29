import os
from copy import deepcopy
from os.path import isfile, join
from typing import Dict, List


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
