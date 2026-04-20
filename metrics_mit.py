import argparse

from analysis_batch import process_batch
from analysis_exports import STANDARD_CSV_HEADER, build_standard_row
from analysis_logging import configure_logging
from DicomParse.utilities import retrieve_dcm_filenames
from ucomx_models import AnalysisMode


def build_parser():
    parser = argparse.ArgumentParser(description="Batch export plan complexity metrics to CSV.")
    parser.add_argument("--input-dir", required=True, help="Directory containing RT Plan DICOM files.")
    parser.add_argument("--output-csv", required=True, help="Output CSV file path.")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search for DICOM files under the input directory.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main():
    args = build_parser().parse_args()
    logger = configure_logging(args.verbose)
    filepaths = retrieve_dcm_filenames(args.input_dir, recursive=args.recursive)

    def metadata_filter(metadata):
        if metadata["beam_type"] not in ["STATIC", "DYNAMIC"]:
            return f"unsupported beam type {metadata['beam_type']}"
        if metadata["rotation_direction"] not in ["CC", "CW"]:
            return f"unsupported rotation direction {metadata['rotation_direction'] or 'N/A'}"
        return None

    process_batch(
        logger=logger,
        filepaths=filepaths,
        output_csv=args.output_csv,
        header=STANDARD_CSV_HEADER,
        build_row=build_standard_row,
        metadata_filter=metadata_filter,
        requested_mode=AnalysisMode.VMAT_IMRT,
    )


if __name__ == '__main__':
    main()
