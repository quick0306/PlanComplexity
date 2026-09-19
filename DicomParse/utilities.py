import os
import os.path as osp
from typing import Callable, List


def retrieve_dcm_filenames(directory: str, recursive: bool = True) -> List:
    """Retrieve file names in a directory."""
    pfiles = []
    for pdir, sub_directory, files in os.walk(directory):
        for file in files:
            filepath = osp.join(pdir, file)
            temp = os.path.basename(filepath)
            if os.path.splitext(temp)[-1] == ".dcm":
                pfiles.append(filepath)
        if not recursive:
            break

    return pfiles


def divide_or_default(a: float, b: float) -> float:
    return a / b if b != 0 else 0.0


def leaf_travel_mcs(leaf_travel: float, mcs: float) -> float:
    """Leaf Travel Modulation Complexity Score (LTMCS)"""
    return ((1000 - leaf_travel) / 1000) * mcs


def retrieve_filenames(directory: str, func: Callable = None, recursive: bool = True, **kwargs) -> List:
    """Retrieve file names in a directory.

    Parameters
    ----------
    directory : str
        The directory to walk over recursively.
    func : function, None
        The function that validates if the file name should be kept.
        If None, no validation will be performed and all file names will be returned.
    recursive : bool
        Whether to search only the root directory.
    kwargs
        Additional arguments passed to the func parameter.
    """
    filenames = []
    if func is None:
        func = lambda x: True
    for pdir, _, files in os.walk(directory):
        for file in files:
            filename = osp.join(pdir, file)
            if func(filename, **kwargs):
                filenames.append(filename)
        if not recursive:
            break
    return filenames
