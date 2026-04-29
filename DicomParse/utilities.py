import os
import os.path as osp
from shutil import copy2

import pydicom

from typing import Callable, List, Union, Tuple


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


def dcm_retrieve(directory: str):
    filepaths = retrieve_dcm_filenames(directory, recursive=True)
    for pfile in filepaths:
        ds = pydicom.dcmread(pfile, force=True)
        try:
            if (str(ds.Modality).upper() == 'RTPLAN') and ('CRT' not in str(ds.RTPlanLabel).upper()):
                if ds.BeamSequence[0].TreatmentMachineName == '2819':
                    copy2(pfile, r"D:\RT_Plan\Axesse")
                elif ds.BeamSequence[0].TreatmentMachineName == '2776':
                    copy2(pfile, r"D:\RT_Plan\Synergy")
                elif ds.BeamSequence[0].TreatmentMachineName == 'TRILOGY-SN5602':
                    copy2(pfile, r"D:\RT_Plan\Trilogy")
                elif ds.BeamSequence[0].TreatmentMachineName == 'TrueBeamSN1352':
                    copy2(pfile, r"D:\RT_Plan\TrueBeam")
                elif ds.BeamSequence[0].TreatmentMachineName == '0210531':
                    copy2(pfile, r"D:\RT_Plan\Tomo")
                elif ds.BeamSequence[0].TreatmentMachineName == '4076':
                    copy2(pfile, r"D:\RT_Plan\VersaHD")
                elif ds.BeamSequence[0].TreatmentMachineName == 'TrueBeamSN2716':
                    copy2(pfile, r"D:\RT_Plan\EDGE")
        except:
            print("RT Plan file has a error: ", pfile)


def ethos_dcm_classify(directory: str):
    """
    通过rtdose找到rtplan, 再由rtplan找到rtss
    :param directory:
    :return:
    """
    filepaths = retrieve_dcm_filenames(directory, recursive=True)
    for rtdose_pfile in filepaths:
        rtdose_ds = pydicom.dcmread(rtdose_pfile, force=True)
        if 'Modality' in rtdose_ds:
            if str(rtdose_ds.Modality).upper() == 'RTDOSE':
                rtplan_uid = rtdose_ds.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID
                rtplan_file = 'RTPLAN.' + rtplan_uid + '.dcm'
                file_dir = os.path.dirname(rtdose_pfile)
                rtplan_filepth = osp.join(file_dir, rtplan_file)

                if rtplan_filepth in filepaths:
                    rtplan_ds = pydicom.dcmread(rtplan_filepth, force=True)

                    if 'Modality' in rtplan_ds and 'RTPlanName' in rtplan_ds:
                        if str(rtplan_ds.Modality).upper() == 'RTPLAN' and 'reconstructed' not in str(
                                rtplan_ds.RTPlanName).lower():
                            rtss_uid = rtplan_ds.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
                            rtss_file = 'RTSTRUCT.' + rtss_uid + '.dcm'
                            rtss_filepath = osp.join(file_dir, rtss_file)

                            drive, path_and_file = os.path.splitdrive(file_dir)
                            ndir = osp.join('D:', path_and_file, rtplan_ds.RTPlanLabel)
                            print(ndir)
                            try:
                                os.makedirs(ndir)
                                copy2(rtdose_pfile, ndir)
                                copy2(rtplan_filepth, ndir)
                                copy2(rtss_filepath, ndir)
                            except OSError as error:
                                print(error)
