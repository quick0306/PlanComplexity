import os
import os.path as osp

from typing import List


def retrieve_dcm_filenames(directory: str, recursive: bool = True) -> List:
    """Retrieve file names in a directory."""
    pfiles = []
    for pdir, _, files in os.walk(directory):
        for file in files:
            filepath = osp.join(pdir, file)
            temp = os.path.basename(filepath)
            if os.path.splitext(temp)[-1] == ".dcm":
                pfiles.append(filepath)
        if not recursive:
            break

    return pfiles
