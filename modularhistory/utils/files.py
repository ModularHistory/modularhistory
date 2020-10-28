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
    for potential_duplicate_file in filenames:
        for filename in reference_filenames:
            should_be_edited = all(
                [
                    filename in potential_duplicate_file,
                    potential_duplicate_file != filename,
                    potential_duplicate_file.startswith(filename[:3]),
                ]
            )
            if should_be_edited:
                duplicate_files = duplicated_files.get(filename) or []
                duplicate_files.append(potential_duplicate_file)
                duplicated_files[filename] = duplicate_files
                # to_edit.append(
                #     (f'sources/{filename}.pdf', f'sources/{filename_copy}.pdf')
                # )
    raise NotImplementedError
    return duplicated_files


def relativize(path: str):
    """Convert the path to a relative path."""
    return join('.', path)
